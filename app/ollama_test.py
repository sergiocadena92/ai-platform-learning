import asyncio

from app.config import get_settings
from app.llm_client import OllamaLLMClient


async def main():
    settings = get_settings()

    client = OllamaLLMClient(
        base_url=settings.ollama_base_url,
        model=settings.ollama_model,
    )

    result = await client.generate(
        prompt=("Explain in one short paragraph " "what a Large Language Model is."),
        temperature=0.7,
        top_p=0.9,
        num_predict=100,
    )

    print(result)


if __name__ == "__main__":
    asyncio.run(main())
