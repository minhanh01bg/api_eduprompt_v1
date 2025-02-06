import re
from fastapi import APIRouter, Depends, Security, UploadFile, File, Form, HTTPException
from app.schemas import schemas
from app.core.security import check_auth_admin
import base64
import io
from pydantic import BaseModel
from app.core.config import settings
from app.core.utils import call_api, extract_assistant_response, cosine_similarity, save_base64_image, random_filename
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

async def generate_caption_from_image(base64_image:str, name:str):
    settings.logger.info(f'Create caption from {name} image')
    img2caption_response = await call_api(API_KEY_ITC, API_URL_ITC, payload={"source": base64_image})
    output_img2caption = img2caption_response.get('output')
    embedding_caption = output_img2caption.get('embedding')
    text = output_img2caption.get('text')
    settings.logger.info(f"Successfully create caption from {name} image")
    return embedding_caption, text

async def embeddings_text(prompt: list, name:str):
    embedding_reponse = await call_api(API_KEY_ITC, API_URL_ITC, payload={"prompt": prompt})
    return embedding_reponse.get('output').get('embeddings')

@router.post('/generate_score_feedback')
async def generate_score_feedback(
    teacher_prompt: str = Form(...),
    student_prompt: str = Form(...),
    teacher_image: UploadFile = File(...),
):
    # generate image for student
    settings.logger.info('Text to image')
    payload = {"prompt": student_prompt}
    text_to_image_response = await call_api(API_KEY_TEXT2IMAGE, API_URL_TEXT2IMAGE, payload=payload)
    # print(api_response)
    try:
        output_t2img = text_to_image_response.get('output')
        base64_student_image = output_t2img.get('image_url')
        
        image_url = f"app/media/{random_filename(extension='png')}"
        save_base64_image(base64_image=base64_student_image, image_url=image_url)

        it2text = await image_text_2text(base64_image=base64_student_image)        

        # create caption from student image
        embedding_student_caption, student_caption = await generate_caption_from_image(base64_image=base64_student_image, name='student')

        # create caption from teacher image
        teacher_file = await teacher_image.read()
        base64_teacher_image = base64.b64encode(teacher_file).decode("utf-8")
        embedding_teacher_caption, teacher_caption = await generate_caption_from_image(base64_image=base64_teacher_image, name='teacher')

        # embedding prompt
        settings.logger.info("Embedding text")
        prompt = [teacher_prompt, student_prompt]
        embeddings_prompt = await embeddings_text(prompt)
        v_teacher_prompt = embeddings_prompt[0]
        v_student_prompt = embeddings_prompt[1]

        cosine_percent = max(0, cosine_similarity(
            v1=v_teacher_prompt, v2=v_student_prompt) * 100)

    except:
        raise HTTPException(status_code=400, detail={
                            'message': "can't generate image on Runpod"})
    return {
        'student_image': image_url,
        'text': it2text,
        'teacher_caption_image': teacher_caption,
        'student_caption_image': student_caption,
        'score_prompt': cosine_percent
    }
