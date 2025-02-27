import aiohttp
from app.core.config import settings
from fastapi import UploadFile
import time

session = None

async def init_session():
    global session
    if session is None:
        session = aiohttp.ClientSession()

async def close_session():
    global session
    if session:
        await session.close()
        session = None

# import requests

# async def call_api(api_key, url, payload):
#     headers = {
#         "Authorization": f"Bearer {api_key}",
#         "Content-Type": "application/json"
#     }

#     response = requests.post(url, json={"input": payload}, headers=headers)
#     return response.json()


async def call_api(api_key, url, payload):
    global session
    if session is None:
        print("Init session")
        await init_session()  # Đảm bảo session đã được khởi tạo

    headers = {"Authorization": f"Bearer {api_key}",
               "Content-Type": "application/json"}
    
    async with session.post(url, json={"input": payload}, headers=headers) as response:
        api_response = await response.json()

    return api_response

import re

def extract_assistant_response(text):
    match = re.search(
    r"<\|start_header_id\|>assistant<\|end_header_id\|>\n\n(.*?)(?:<\|eot_id\|>|$)", text, re.DOTALL
)
    if match:
        return match.group(1).strip()  # Lấy nội dung của assistant
    return None

import uuid
from datetime import datetime
def random_filename(extension='png'):
    timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')

    return f"{timestamp}_{uuid.uuid4().hex}.{extension}"


import numpy as np
def cosine_similarity(v1, v2):
    dot_product = np.dot(v1,v2)
    norm_v1 = np.linalg.norm(v1)
    norm_v2 = np.linalg.norm(v2)
    return dot_product / (norm_v1 * norm_v2)


from PIL import Image
import base64, io
def save_base64_image(base64_image:str, image_url: str):
    Image.open(io.BytesIO(base64.b64decode(base64_image))).save(image_url)


async def image_text_2text(base64_image: str):
    settings.logger.info('Create text from image and text')
    payload_imgtext2img = {"prompt": settings.PROMPT_CONFIG_IMAGE_TEXT_2IMAGE,
                           "source": base64_image}
    imgtxt2image_response = await call_api(settings.API_KEY_VMH, settings.API_URL_ITT, payload=payload_imgtext2img)
    output_it2txt = imgtxt2image_response.get('output')
    it2text = output_it2txt.get('text')
    print(f"Log image to caption: {it2text}")
    it2text = extract_assistant_response(it2text)
    return it2text


async def convert_to_base64(file: UploadFile):
    # Read the uploaded file as bytes
    image_bytes = await file.read()

    # Convert bytes to base64 string
    base64_str = base64.b64encode(image_bytes).decode("utf-8")

    return base64_str
