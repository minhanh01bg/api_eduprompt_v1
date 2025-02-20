import shutil
from pydantic import BaseModel
import re
from fastapi import APIRouter, Depends, Security, UploadFile, File, Form, HTTPException, status
from app.schemas import schemas
from app.core.security import check_auth_admin
import base64
import io
from app.schemas.runpod_schemas import APIRequest, RequestBodyPrompt
from app.schemas.prompt_schemas import Generate_prompt, Generate_image
from app.core.config import settings
from app.core.utils import call_api
from app.core.chat_openai import sent_message
from app.core.utils import save_base64_image, random_filename


router = APIRouter()


# @router.get('/')
# async def home(current_user: schemas.User = Security(check_auth_admin)):
#     return {'message': '/home'}

API_URL_ITT = 'https://api.runpod.ai/v2/h2zfmy7vokxl8x/runsync'
API_KEY_VMH = 'O461H84OAYQK5UG9K5C24AR7XHMDRDEFSXCW4B5T'

API_URL_ITC = 'https://api.runpod.ai/v2/iwupjthns1gw11/runsync'
API_KEY_ITC = 'rpa_7DWIWXV9FLMKPRA01519O44QW7Q0NKR2QYU7RULC12ygum'

API_URL_TEXT2IMAGE = 'https://api.runpod.ai/v2/7wt9c65qtmm1uj/runsync'
API_KEY_TEXT2IMAGE = 'rpa_7DWIWXV9FLMKPRA01519O44QW7Q0NKR2QYU7RULC12ygum'

API_URL_TEXT2IMAGE2 = 'https://api.runpod.ai/v2/pyrat8v5lumbfb/runsync'
API_KEY_TEXT2IMAGE2 = 'O461H84OAYQK5UG9K5C24AR7XHMDRDEFSXCW4B5T'


@router.post('/generate_prompt', status_code=status.HTTP_200_OK)
async def generate_prompt(data: Generate_prompt):
    settings.logger.info(f'Start generating prompt: {data}')
    complexity_instruction = "The lenght cannot be more than 50 tokens.Create a simple and short prompt with minimal details."
    if "Beginner" in data.level:
        complexity_instruction = "The lenght cannot be more than 50 tokens.Create a simple and short prompt with minimal details."
    elif "Intermediate" in data.level:
        complexity_instruction = "The lenght cannot be more than 77 tokens.Create a moderately descriptive prompt with some complexity by combining multiple ideas like style, objects, and mood."
    elif "Advanced" in data.level:
        complexity_instruction = "The lenght cannot be more than 150 tokens .Create a highly detailed and professional-quality prompt. Include nuanced details.Should be written in one passage."

    ai_instruction = (
        f"You are a professional prompt engineer specializing in creating creative, detailed, and structured prompts "
        f"for AI image generation tool Stable diffusion 3.5. Your job is to use the provided keywords and generate an example "
        f"of a well-crafted image-generation prompt. Adjust the complexity based on the following instruction: {complexity_instruction}."
    )

    keywords = ""
    if data.theme:
        keywords += f"data.Theme: {', '.join(data.theme)}. "
    if data.mood:
        keywords += f"Mood: {', '.join(data.mood)}. "
    if data.characters:
        keywords += f"Characters: {', '.join(data.characters)}. "
    if data.context:
        keywords += f"Context: {', '.join(data.context)}. "
    if data.art_medium:
        keywords += f"Art Medium: {', '.join(data.art_medium)}. "
    if data.color_scheme:
        keywords += f"Color Scheme: {', '.join(data.color_scheme)}. "
    if data.shot_type:
        keywords += f"Shot Type: {', '.join(data.shot_type)}. "
    if data.actions_details:
        keywords += f"Details: {data.actions_details}. "
    if data.negative_prompt:
        keywords += f"Exclude: {data.negative_prompt}. "

    full_prompt = f"{ai_instruction}\n\nKeywords:\n{keywords}\n\nGenerate an example of a stable diffusion prompt based on these keywords."

    prompt = sent_message(full_prompt)
    return prompt


@router.post('/generate_image', status_code=status.HTTP_200_OK)
async def generate_image(data: Generate_image):
    settings.logger.info('Start generating image')
    payload = {"prompt": data.prompt,
               "label": "teacher",
               "width": 1024,
               "height": 1024,
               "num_inference_steps": 50,
               }
    text_to_image_response = await call_api(API_KEY_TEXT2IMAGE, API_URL_TEXT2IMAGE, payload=payload)

    if text_to_image_response.get('status') == 'COMPLETED':
        try:
            images = text_to_image_response.get('output').get('image_urls')
            results = []
            for img in images:
                file_name = random_filename(extension='png')
                url = f"{settings.DOMAIN}/app/media/{file_name}"
                save_base64_image(img, f"app/media/{file_name}")
                results.append(url)

            settings.logger.info('Successfully generate image')
            return {"image_urls": results}
        except:
            raise HTTPException(
                status_code=400, detail="Error server not image_url in response")
    elif text_to_image_response.get('status') != 'COMPLETED':
        raise HTTPException(
            status_code=400, detail="Error in generating image")


class ImageUploadRequest(BaseModel):
    images: list[str]


@router.post('/upload_image_base64', status_code=status.HTTP_200_OK)
async def upload_images(images: list[UploadFile] = File(...)):
    settings.logger.info('Start uploading images')

    image_urls = []
    try:
        for image in images:
            image_path = f"app/media/{random_filename(extension='png')}"
            with open(image_path, "wb") as buffer:
                shutil.copyfileobj(image.file, buffer)
            image_urls.append(f"{settings.DOMAIN}/{image_path}")

        settings.logger.info('Successfully uploaded images')
    except Exception as e:
        raise HTTPException(
            status_code=400, detail=f"Error in uploading images: {str(e)}")

    return {"image_urls": image_urls}
