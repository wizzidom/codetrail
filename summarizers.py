# import os
# import ollama
# import asyncio
# import functools
# import time
# from typing import Literal

# # Optional: If you’re planning to use OpenAI later
# # from openai import AsyncOpenAI
# # openai_client = AsyncOpenAI()

# MODE: Literal["ollama", "openai"] = os.getenv("MODEL_PROVIDER", "ollama")

# async def summarize_with_ollama(function_code: str) -> str:
#     prompt = f"Summarize this Python function in one sentence:\n\n{function_code}"
#     loop = asyncio.get_running_loop()
#     func = functools.partial(
#         ollama.chat,
#         model='phi',
#         messages=[{"role": "user", "content": prompt}]
#     )
#     start = time.perf_counter()
#     response = await loop.run_in_executor(None, func)
#     end = time.perf_counter()
#     print(f"Ollama call took {end - start:.2f} seconds")
#     return response['message']['content'].strip()

# # Optional: placeholder if you’ll use OpenAI later
# # async def summarize_with_openai(function_code: str) -> str:
# #     response = await openai_client.chat.completions.create(
# #         model="gpt-4o",
# #         messages=[{"role": "user", "content": f"Summarize this Python function:\n{function_code}"}],
# #         max_tokens=60,
# #         temperature=0.2
# #     )
# #     return response.choices[0].message.content.strip()

# # Main interface used by the rest of your app
# async def generate_function_summary(function_code: str) -> str:
#     if MODE == "ollama":
#         return await summarize_with_ollama(function_code)
#     # elif MODE == "openai":
#     #     return await summarize_with_openai(function_code)
#     else:
#         return "No valid summarization backend selected."

import os
import ollama
import asyncio
import functools
import time
from typing import Literal

MODE: Literal["ollama", "openai"] = os.getenv("MODEL_PROVIDER", "ollama")

async def summarize_with_ollama(function_code: str) -> str:
    prompt = f"Summarize this Python function in one sentence:\n\n{function_code}"
    loop = asyncio.get_running_loop()
    func = functools.partial(
        ollama.chat,
        model='phi',
        messages=[{"role": "user", "content": prompt}]
    )
    try:
        start = time.perf_counter()
        response = await loop.run_in_executor(None, func)
        end = time.perf_counter()
        print(f"Ollama call took {end - start:.2f} seconds")
        return response['message']['content'].strip()
    except Exception as e:
        print(f"Error calling Ollama: {e}")
        return "Summary unavailable due to service error."

async def generate_function_summary(function_code: str) -> str:
    if MODE == "ollama":
        return await summarize_with_ollama(function_code)
    else:
        return "No valid summarization backend selected."
