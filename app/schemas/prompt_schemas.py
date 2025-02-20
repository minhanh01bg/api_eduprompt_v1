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

class Generate_image(BaseModel):
    # 'A whimsical and creative image depicting a hybrid creature that is a mix of a waffle and a hippopotamus, basking in a river of melted butter amidst a breakfast-themed landscape. It features the distinctive, bulky body shape of a hippo. However, instead of the usual grey skin, the creature’s body resembles a golden-brown, crispy waffle fresh off the griddle. The skin is textured with the familiar grid pattern of a waffle, each square filled with a glistening sheen of syrup. The environment combines the natural habitat of a hippo with elements of a breakfast table setting, a river of warm, melted butter, with oversized utensils or plates peeking out from the lush, pancake-like foliage in the background, a towering pepper mill standing in for a tree.  As the sun rises in this fantastical world, it casts a warm, buttery glow over the scene. The creature, content in its butter river, lets out a yawn. Nearby, a flock of birds take flight'
    prompt: str