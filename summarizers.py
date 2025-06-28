import os
import ollama
from typing import Literal

# Optional: If you’re planning to use OpenAI later
# from openai import AsyncOpenAI
# openai_client = AsyncOpenAI()

MODE: Literal["ollama", "openai"] = os.getenv("MODEL_PROVIDER", "ollama")

async def summarize_with_ollama(function_code: str) -> str:
    prompt = f"Summarize this Python function in one sentence:\n\n{function_code}"
    response = ollama.chat(
        model='phi',
        messages=[{"role": "user", "content": prompt}]
    )
    return response['message']['content'].strip()

# Optional: placeholder if you’ll use OpenAI later
# async def summarize_with_openai(function_code: str) -> str:
#     response = await openai_client.chat.completions.create(
#         model="gpt-4o",
#         messages=[{"role": "user", "content": f"Summarize this Python function:\n{function_code}"}],
#         max_tokens=60,
#         temperature=0.2
#     )
#     return response.choices[0].message.content.strip()

# Main interface used by the rest of your app
async def generate_function_summary(function_code: str) -> str:
    if MODE == "ollama":
        return await summarize_with_ollama(function_code)
    # elif MODE == "openai":
    #     return await summarize_with_openai(function_code)
    else:
        return "No valid summarization backend selected."
