import re
from fastapi import APIRouter, Depends, Security, UploadFile, File, Form, HTTPException
from app.schemas import schemas
from app.core.security import check_auth_admin
import base64
import io
from pydantic import BaseModel
from app.core.config import settings
from app.core.utils import call_api, extract_assistant_response, cosine_similarity, save_base64_image, random_filename
from app.core.chat_openai import get_feedback
from PIL import Image
router = APIRouter()

API_URL_ITT = 'https://api.runpod.ai/v2/h2zfmy7vokxl8x/runsync'
API_KEY_VMH = 'O461H84OAYQK5UG9K5C24AR7XHMDRDEFSXCW4B5T'

API_URL_ITC = 'https://api.runpod.ai/v2/iwupjthns1gw11/runsync'
API_KEY_ITC = 'rpa_7DWIWXV9FLMKPRA01519O44QW7Q0NKR2QYU7RULC12ygum'

API_URL_TEXT2IMAGE = 'https://api.runpod.ai/v2/7wt9c65qtmm1uj/runsync'
API_KEY_TEXT2IMAGE = 'rpa_7DWIWXV9FLMKPRA01519O44QW7Q0NKR2QYU7RULC12ygum'


async def image_text_2text(base64_image: str):
    settings.logger.info('Create text from image and text')
    payload_imgtext2img = {"prompt": settings.PROMPT_CONFIG_IMAGE_TEXT_2IMAGE,
                           "source": base64_image}
    imgtxt2image_response = await call_api(API_KEY_VMH, API_URL_ITT, payload=payload_imgtext2img)
    output_it2txt = imgtxt2image_response.get('output')
    it2text = output_it2txt.get('text')
    it2text = extract_assistant_response(it2text)
    settings.logger.info('Successfully create text from image and text')
    return it2text


async def generate_caption_from_image(base64_image: str, name: str):
    settings.logger.info(f'Create caption from {name} image')
    img2caption_response = await call_api(API_KEY_ITC, API_URL_ITC, payload={"source": base64_image})
    output_img2caption = img2caption_response.get('output')
    embedding_caption = output_img2caption.get('embeddings')
    text = output_img2caption.get('text')
    settings.logger.info(f"Successfully create caption from {name} image")
    return embedding_caption, text


async def embeddings_text(prompt: str):
    embedding_reponse = await call_api(API_KEY_ITC, API_URL_ITC, payload={"prompt": prompt})
    return embedding_reponse.get('output').get('embeddings')


@router.post('/generate_score_feedback')
async def generate_score_feedback(
    teacher_prompt: str = Form(...),
    student_prompt: str = Form(...),
    teacher_image: UploadFile = File(...),
):
    # generate image for student
    try:
        settings.logger.info('Text to image')
        payload = {"prompt": student_prompt, "label": "student"}
        text_to_image_response = await call_api(API_KEY_TEXT2IMAGE, API_URL_TEXT2IMAGE, payload=payload)
        # print(api_response)
    except:
        raise HTTPException(status_code=400, detail={
                            'message': "can't generate image on Runpod"})
    # image + text to text
    try:
        output_t2img = text_to_image_response.get('output')
        base64_student_image = output_t2img.get('image_url')
        
        image_url = f"app/media/{random_filename(extension='png')}"
        save_base64_image(base64_image=base64_student_image,
                          image_url=image_url)

        it2text = await image_text_2text(base64_image=base64_student_image)
    except:
        raise HTTPException(status_code=400, detail={
                            'message': "can't create text from image and text on Runpod"})
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

    # calculate cosine similarity
    try:
        settings.logger.info("Scoring")
        prompt = [teacher_prompt, student_prompt]
        embeddings_prompt = await embeddings_text(prompt=prompt)
        # print(embeddings_prompt)
        v_teacher_prompt = embeddings_prompt[0]
        v_student_prompt = embeddings_prompt[1]

        cosine_prompt_percent = max(0, cosine_similarity(
            v1=v_teacher_prompt, v2=v_student_prompt) * 100)

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
    except:
        raise HTTPException(status_code=400, detail={
                            'message': "can't calculate cosine similarity"})
    try:
        settings.logger.info("Feedback")

        prompt_feedback = f"Compare the following prompts and captions to provide feedback for the student on how to improve their prompt.\n\n"
        prompt_feedback += f"Teacher's Prompt: {teacher_prompt}\n"
        prompt_feedback += f"Student's Prompt: {student_prompt}\n\n"
        prompt_feedback += f"Teacher's Image Caption: {teacher_caption}\n"
        prompt_feedback += f"Student's Image Caption: {student_caption}\n"
        prompt_feedback += f"Student's Image Description: {it2text}\n\n"
        prompt_feedback += f"Instruction:\n\n"
        prompt_feedback += f"Identify missing or unclear details in the student's prompt compared to the teacher's prompt.\n"
        prompt_feedback += f"Analyze how these differences affect the generated image.\n"
        prompt_feedback += f"Suggest specific improvements to make the student's prompt more detailed, accurate, or stylistically consistent with the teacher's prompt.\n"
        prompt_feedback += f"Please give feedback based on the information you have without mentioning this information in your answer.\n"
        prompt_feedback += ("Don't mention the teacher's prompt, just focus on responding to the student's prompt: for example:\n"
                            "1. Subject Similarity: Both images feature a bird (Partridge and Chicken) as a focal point, but the type and presentation are different.\n"
                            "2. Artistic Style: The first image uses a primitivist style with abstract shapes and earthy colors, whereas the second image uses a realistic style with vivid colors and realistic lighting.\n"
                            "3. Composition: The first image has a whimsical, pattern-filled backdrop, while the second highlights a more realistic landscape; both include the sun, but their representations differ significantly.")
        feedback = get_feedback(prompt=prompt_feedback)
        settings.logger.info("Successfully feedback")
    except:
        raise HTTPException(status_code=400, detail={
                            'message': "can't feedback"})
    return {
        'student_image': image_url,
        'text': it2text,
        'teacher_caption_image': teacher_caption,
        'student_caption_image': student_caption,
        'score': score,
        'feedback': feedback
    }
