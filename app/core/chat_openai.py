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
            "You are a professional stable diffusion prompt engineer.",
        ),
        ("human", prompt),
    ]
    ai_msg = llm.invoke(messages)
    print(ai_msg)
    return ai_msg.content

def get_feedback(prompt):
    messages =[
        ("system", "You are an AI assistant designed to help students improve their AI-generated image prompts. Your goal is to analyze the prompt written by the student and compare it with the reference prompt provided by the teacher. You should identify any differences or missing elements that could affect the final image. Use the captions generated from both the teacher's and the student's images, as well as the additional description from the student's image, to provide detailed feedback. Focus on aspects like clarity, detail, style, composition, and specific objects or actions described. Be constructive and guide the student on how to improve their prompt to better match the reference."),
        ("human", prompt)
    ]
    ai_msg = llm.invoke(messages)
    return ai_msg.content