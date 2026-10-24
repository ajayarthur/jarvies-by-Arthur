from groq import Groq
import os
from livekit.agents import function_tool

client = Groq(api_key=os.getenv("GROQ_API_KEY"))

@function_tool
async def groq_answer_tool(query: str) -> str:
    """
    Fast study answer using Groq LLaMA or Mixtral
    """
    try:
        response = client.chat.completions.create(
            model="mixtral-8x7b-32768",  # super fast + very powerful
            messages=[
                {"role": "system", "content": "You are a fast study assistant."},
                {"role": "user", "content": query}
            ],
            max_tokens=500,
            temperature=0.1
        )

        return response.choices[0].message["content"]

    except Exception as e:
        return f"❌ Groq Error: {e}"
