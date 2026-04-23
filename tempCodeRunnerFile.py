from langchain_core.prompts import PromptTemplate
from langchain_ollama import OllamaLLM

model = OllamaLLM(model="mistral")

def Script(content_type, topic, emotion):

    promptTemplate = PromptTemplate(
        template="""
You are a viral short-form content creator.

Write a READY-TO-POST {content_type} script about "{topic}"

Emotion: {emotion}

STRICT RULES:
- EXACTLY 10-12 lines
- Each line under 10 words
- Conversational
- No explanations

STYLE:
- First line = hook
- Use emotion
- Add emojis
- End with CTA

OUTPUT:
Only the script. Nothing else.
""",
        input_variables=["content_type", "topic", "emotion"]
    )

    prompt = promptTemplate.format(
        content_type=content_type,
        topic=topic,
        emotion=emotion
    )

    response = model.invoke(prompt)

    return response.strip()