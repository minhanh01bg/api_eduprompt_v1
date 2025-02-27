import re
from fastapi import APIRouter, Depends, Security, UploadFile, File, Form, HTTPException
from app.schemas import schemas
from app.core.security import check_auth_admin
import base64
import io
from pydantic import BaseModel
from app.core.config import settings
from app.core.utils import call_api,  cosine_similarity, image_text_2text, convert_to_base64
from app.core.chat_openai import get_feedback
from PIL import Image
import time
import re

router = APIRouter()

# test
async def generate_caption_from_image(base64_image: str, name: str):
    settings.logger.info(f'Create caption from {name} image')
    img2caption_response = await call_api(settings.API_KEY_HIEUVM, settings.API_URL_ITC, payload={"source": base64_image})
    output_img2caption = img2caption_response.get('output')
    embedding_caption = output_img2caption.get('embeddings')
    text = output_img2caption.get('text')
    settings.logger.info(f"Successfully create caption from {name} image")
    return embedding_caption, text

# test
async def embeddings_text(prompt: str):
    embedding_reponse = await call_api(settings.API_KEY_HIEUVM, settings.API_URL_ITC, payload={"prompt": prompt})
    return embedding_reponse.get('output').get('embeddings')

# test
async def scoring_similarity(teacher_prompt, student_prompt, teacher_image, base64_student_image):
    # image to caption
    try:
        # create caption from student image
        embedding_student_caption, student_caption = await generate_caption_from_image(base64_image=base64_student_image, name='student')
    except:
        raise HTTPException(status_code=400, detail={
                            'message': "can't create caption from image on Runpod"})

    # teacher image to caption
    try:
        # create caption from teacher image
        teacher_file = await teacher_image.read()
        base64_teacher_image = base64.b64encode(teacher_file).decode("utf-8")
        embedding_teacher_caption, teacher_caption = await generate_caption_from_image(base64_image=base64_teacher_image, name='teacher')

    except:
        raise HTTPException(status_code=400, detail={
                            'message': "can't generate image on Runpod"})

    prompt = [teacher_prompt, student_prompt]
    embeddings_prompt = await embeddings_text(prompt=prompt)
    v_teacher_prompt = embeddings_prompt[0]
    v_student_prompt = embeddings_prompt[1]
    cosine_prompt_percent = max(0, cosine_similarity(
        v1=v_teacher_prompt, v2=v_student_prompt) * 100)

    cosine_caption_percent = max(0, cosine_similarity(
        v1=embedding_teacher_caption, v2=embedding_student_caption) * 100)

    cosine_caption_percent = max(0, cosine_similarity(
        v1=embedding_teacher_caption, v2=embedding_student_caption) * 100)
    cosine_teacher_student = max(0, cosine_similarity(
        v1=embedding_teacher_caption, v2=v_student_prompt) * 100)
    cosine_student_teacher = max(0, cosine_similarity(
        v1=embedding_student_caption, v2=v_teacher_prompt) * 100)

    score = settings.PROMPT_WEIGHT * cosine_prompt_percent + settings.CAPTION_WEIGHT * cosine_caption_percent + \
        settings.PROMPT_CAPTION_WEIGHT * \
        (cosine_teacher_student + cosine_student_teacher) / 2
    settings.logger.info("Successfully scoring")
    return score



@router.post('/generate_score_feedback')
async def generate_score_feedback(
    teacher_caption: str = Form(...),
    teacher_prompt: str = Form(...),
    student_prompt: str = Form(...),
    # teacher_image: UploadFile = File(...),
    student_image: UploadFile = File(...),
):
    _start = time.time()
    settings.logger.info("Get caption from student image")
    try:
        base64_student_image = await convert_to_base64(student_image)
        it2text_student = await image_text_2text(base64_image=base64_student_image)
    except:
        raise HTTPException(status_code=400, detail={
                            'message': "can't create text from student image and text on Runpod"})

    try:
        settings.logger.info("Feedback")

        prompt_feedback = (f"Compare the following prompts and captions to provide feedback and score for the student on how to improve their prompt.\n\n"
                           "Compare these prompts and give a score of how much the student's prompt aligns with the teacher's prompt out of 100. "
                           "The score should be over 90 if the main elements (subject, key features, surroundings, and style) are present and similar. "
                           "If the prompts describe very different concepts, the score should be below 10. "
                           f"The score should be over 90 if the main elements (subject, key features, surroundings, and style) are present and similar. "
                           f"Teacher's Prompt: {teacher_prompt}\n"
                           f"Student's Prompt: {student_prompt}\n\n"
                           #    f"Teacher's Image Caption: {teacher_caption}\n"
                           #    f"Student's Image Caption: {student_caption}\n"
                           f"Teacher's Image Description: {teacher_caption}\n\n"
                           f"Student's Image Description: {it2text_student}\n\n"
                           f"Instruction:\n\n"
                           f"Identify missing or unclear details in the student's prompt compared to the teacher's prompt.\n"
                           f"Analyze how these differences affect the generated image.\n"
                           f"Suggest specific improvements to make the student's prompt more detailed, accurate, or stylistically consistent with the teacher's prompt.\n")

        prompt_feedback += (f"Please give feedback based on the information you have without mentioning this information in your answer.\n"
                            "Don't mention the teacher's prompt, just focus on responding to the student's prompt: for example:\n"
                            "Score = 55 \n"
                            "Feedback\n"
                            "1. Subject Similarity: Both images feature a bird (Partridge and Chicken) as a focal point, but the type and presentation are different.\n"
                            "2. Artistic Style: The first image uses a primitivist style with abstract shapes and earthy colors, whereas the second image uses a realistic style with vivid colors and realistic lighting.\n"
                            "3. Composition: The first image has a whimsical, pattern-filled backdrop, while the second highlights a more realistic landscape; both include the sun, but their representations differ significantly.")

        feedback = get_feedback(prompt=prompt_feedback)
        match = re.search(r"Score\s*=\s*(\d+)", feedback)
        score = int(match.group(1))
        settings.logger.info("Successfully feedback")
    except:
        raise HTTPException(status_code=400, detail={
                            'message': "can't feedback"})
    
    _end = time.time() - _start
    settings.logger.info(f'Score and feedback - Excution time: {_end:.2f}')
    return {
        'student_caption': it2text_student,
        'score': score,
        'feedback': feedback,
        'excution_time': f'{_end:.2f}'
    }
