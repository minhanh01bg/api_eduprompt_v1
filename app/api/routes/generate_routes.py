import shutil
from pydantic import BaseModel
import re
from fastapi import APIRouter, Depends, Security, UploadFile, File, Form, HTTPException, status
from app.schemas import schemas
from app.core.security import check_auth_admin
import base64
import io
from app.schemas.runpod_schemas import APIRequest, RequestBodyPrompt
from app.schemas.prompt_schemas import Generate_prompt, Generate_image, Enhance_prompt
from app.core.config import settings
from app.core.utils import call_api
from app.core.chat_openai import sent_message, enhance_message
from app.core.utils import save_base64_image, random_filename
import json

router = APIRouter()

prompt_text = """
{
  "3": {
    "inputs": {
      "seed": 432927437327497,
      "steps": 20,
      "cfg": 8.1,
      "sampler_name": "euler",
      "scheduler": "normal",
      "denoise": 1,
      "model": [
        "4",
        0
      ],
      "positive": [
        "6",
        0
      ],
      "negative": [
        "7",
        0
      ],
      "latent_image": [
        "5",
        0
      ]
    },
    "class_type": "KSampler",
    "_meta": {
      "title": "KSampler"
    }
  },
  "4": {
    "inputs": {
      "ckpt_name": "dynavisionXLAllInOneStylized_releaseV0610Bakedvae.safetensors"
    },
    "class_type": "CheckpointLoaderSimple",
    "_meta": {
      "title": "Load Checkpoint"
    }
  },
  "5": {
    "inputs": {
      "width": 1024,
      "height": 1024,
      "batch_size": 1
    },
    "class_type": "EmptyLatentImage",
    "_meta": {
      "title": "Empty Latent Image"
    }
  },
  "6": {
    "inputs": {
      "text": "Het meisje met de parel, Johannes Vermeer",
      "clip": [
        "4",
        1
      ]
    },
    "class_type": "CLIPTextEncode",
    "_meta": {
      "title": "CLIP Text Encode (Positive Prompt)"
    }
  },
  "7": {
    "inputs": {
      "text": "text, watermark",
      "clip": [
        "4",
        1
      ]
    },
    "class_type": "CLIPTextEncode",
    "_meta": {
      "title": "CLIP Text Encode (Negative Prompt)"
    }
  },
  "8": {
    "inputs": {
      "samples": [
        "3",
        0
      ],
      "vae": [
        "4",
        2
      ]
    },
    "class_type": "VAEDecode",
    "_meta": {
      "title": "VAE Decode"
    }
  },
  "9": {
    "inputs": {
      "filename_prefix": "ComfyUI",
      "images": [
        "8",
        0
      ]
    },
    "class_type": "SaveImage",
    "_meta": {
      "title": "Save Image"
    }
  }
}
"""


def get_prompt(prompt: str, number_image: int = 1):
    data = json.loads(prompt_text)
    data['6']['inputs']['text'] = prompt
    data['5']['inputs']['batch_size'] = number_image
    return data


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
    prompt = data.prompt
    number_image = data.number_image
    payload_data = get_prompt(prompt,number_image=number_image)
    payload = {
        "prompt": payload_data,
    }

    text_to_image_response = await call_api(settings.API_KEY_HIEUVM, settings.API_URL_TEXT2IMAGE_DYNA, payload=payload)

    if text_to_image_response.get('status') == 'COMPLETED':
        try:
            images = text_to_image_response.get('output').get('images')
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

@router.post('/enhance_prompt', status_code=status.HTTP_200_OK)
async def enhance_prompt(data: Enhance_prompt):
    prompt = data.prompt
    enhance = enhance_message(prompt)
    return enhance