import re
from fastapi import APIRouter, Depends, Security, UploadFile, File, Form, HTTPException
from app.schemas import schemas
from app.core.security import check_auth_admin
import base64
import io
from app.schemas.runpod_schemas import APIRequest, RequestBodyPrompt
from app.schemas.prompt_schemas import Generate_prompt
from app.core.config import settings
from app.core.utils import call_api
from app.core.chat_openai import sent_message
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

@router.post('/generate_prompt')
async def generate_prompt(data: Generate_prompt):
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

@router.post('/generate_image')
async def generate_image(prompt: str = Form(...)):
    payload = {"prompt": prompt}
    text_to_image_response = await call_api(API_KEY_TEXT2IMAGE, API_URL_TEXT2IMAGE, payload=payload)
    return text_to_image_response
