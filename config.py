import os
from dotenv import load_dotenv

load_dotenv(override=True)


def get_llm(temperature: float = 0):
    """Returns the configured LLM instance based on ENV in .env."""
    env = os.getenv("ENV", "development")

    if env == "production":
        # OpenAI (GPT-4o or gpt-4o-mini)
        from langchain_openai import ChatOpenAI
        model = os.getenv("OPENAI_MODEL", "gpt-4o-mini")
        return ChatOpenAI(model=model, temperature=temperature)

    else:
        # Local Ollama (Free, offline, for testing graph logic)
        from langchain_ollama import ChatOllama
        model_name = os.getenv("OLLAMA_MODEL", "qwen2.5-coder:3b")
        return ChatOllama(model=model_name, temperature=temperature)