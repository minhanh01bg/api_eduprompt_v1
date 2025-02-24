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

@router.post('/image_text_to_text')
async def image_text_to_text(
    prompt: str = Form(...),
    image: UploadFile = File(...),
):
    file_content = await image.read()
    base64_image = base64.b64encode(file_content).decode("utf-8")
    payload = {"prompt": prompt, "source": base64_image}
    import json
    with open('./test.json', 'w', encoding='utf-8') as f:
        json.dump({"input": payload}, f, ensure_ascii=False, indent=4)

    api_response = await call_api(settings.API_KEY_VMH, settings.API_URL_ITT, payload=payload)
    return {"api_response": api_response}

# @router.post('/image_to_caption')
# async def image_to_caption(
#     image: UploadFile = File(...),
# ):
#     file_content = await image.read()
#     base64_image = base64.b64encode(file_content).decode('utf-8')
#     payload = {"source": base64_image}

#     import json
#     with open('./test.json', 'w', encoding='utf-8') as f:
#         json.dump({"input": payload}, f, ensure_ascii=False, indent=4)

#     api_response = await call_api(API_KEY_ITC, API_URL_ITC, payload=payload)
#     return {"api_response": api_response}


# @router.post('/prompt_embedding')
# async def test_prompt_embedding(prompt1: str, prompt2: str):
#     prompt = [prompt1, prompt2]
#     embedding_reponse = await call_api(API_KEY_ITC, API_URL_ITC, payload={"prompt": prompt})
#     return embedding_reponse.get('output').get('embeddings')[0]