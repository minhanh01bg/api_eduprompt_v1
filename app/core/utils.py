import aiohttp

async def call_api(api_key, url, payload):
    headers = {"Authorization": f"Bearer {api_key}",
               "Content-Type": "application/json"}

    async with aiohttp.ClientSession() as session:
        async with session.post(url, json={"input": payload}, headers=headers) as response:
            api_response = await response.json()

    return api_response

import re

def extract_assistant_response(text):
    match = re.search(
        r"<\|start_header_id\|>assistant<\|end_header_id\|>\n\n(.*?)<\|eot_id\|>", text, re.DOTALL)
    if match:
        return match.group(1).strip()  # Lấy nội dung của assistant
    return None

import uuid

def random_filename(extension='png'):
    return f"{uuid.uuid4().hex}.{extension}"


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