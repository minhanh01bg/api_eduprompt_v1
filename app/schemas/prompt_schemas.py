from pydantic import BaseModel

# class Generate_prompt(BaseModel):
#     level: str = 'Beginner'
#     theme: str = 'Nature'
#     mood: str = 'Joyful'
#     characters: str = 'Animals'
#     context: str = 'Outdoor'
#     art_medium: str = 'Graffiti'
#     color_scheme: str = 'Vibrant'
#     shot_type: str = 'Close-up'
#     actions_details: str = 'Animals playing joyfully in a vibrant outdoor setting'
#     negative_prompt: str = 'No dark colors, no sad expressions, no urban elements'


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