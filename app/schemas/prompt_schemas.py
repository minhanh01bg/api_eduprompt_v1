from pydantic import BaseModel

class Generate_prompt(BaseModel):
    level: str
    theme: str
    mood: str
    characters: str
    context: str
    art_medium: str
    color_scheme: str
    shot_type: str
    actions_details: str
    negative_prompt: str
