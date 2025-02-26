from langchain_openai import ChatOpenAI
import getpass
import os

os.environ["OPENAI_API_KEY"] = "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"


llm = ChatOpenAI(
    model="gpt-4o-mini",
    # temperature=0,
    max_tokens=200,
    # timeout=None,
    # max_retries=2,
)


def sent_message(prompt):
    messages = [
        (
            "system",
            "You are a professional stable diffusion prompt engineer. Don't return answers with single or double quotes at the beginning and end of the sentence. You do not need to return additional quotation marks for the entire sentence.",
        ),
        ("human", prompt),
    ]
    ai_msg = llm.invoke(messages)
    # print(ai_msg)
    return ai_msg.content


def get_feedback(prompt):
    messages = [
        ("system", "You are an AI assistant designed to help students improve their AI-generated image prompts. Your goal is to analyze the prompt written by the student and compare it with the reference prompt provided by the teacher. You should identify any differences or missing elements that could affect the final image. Use the captions generated from both the teacher's and the student's images, as well as the additional description from the student's image, to provide detailed feedback. Focus on aspects like clarity, detail, style, composition, and specific objects or actions described. Be constructive and guide the student on how to improve their prompt to better match the reference."),
        ("human", prompt)
    ]
    ai_msg = llm.invoke(messages)
    return ai_msg.content


def enhance_message(prompt):
    system_prompt = (
    "You are an AI that enhances user prompts by expanding them with vivid details while maintaining their original meaning. Your task is to rewrite the user's prompt into a more descriptive, imaginative, and engaging version. Add relevant details such as colors, emotions, settings, and interactions to create a richer and more compelling prompt."
    "Don't write the prompt too long, adjust it based on the amount of information the user gives you. Do not write more than 60 tokens."
    "Write a prompt for children"
    "You do not need to return additional quotation marks for the entire sentence."
    )
    messages = [
        ("system", system_prompt),
        ("human", prompt),
    ]
    ai_msg = llm.invoke(messages)
    # print(ai_msg)
    return ai_msg.content
