from pydantic import BaseModel

class Generate_prompt(BaseModel):
    level: str = 'Beginner'
    theme: str = 'Nature'
    mood: str = 'Joyful'
    characters: str = 'Animals'
    context: str = 'Outdoor'
    art_medium: str = 'Graffiti'
    color_scheme: str = 'Vibrant'
    shot_type: str = 'Close-up'
    actions_details: str = 'Animals playing joyfully in a vibrant outdoor setting'
    negative_prompt: str = 'No dark colors, no sad expressions, no urban elements'
