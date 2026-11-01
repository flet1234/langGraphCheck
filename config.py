import os
from dotenv import load_dotenv

# Loads variables from .env into os.environ
load_dotenv()


def get_llm(temperature: float = 0):
    """Returns the configured LLM instance based on ENV."""
    env = os.getenv("ENV", "development")

    if env == "production":
        from langchain_openai import ChatOpenAI
        return ChatOpenAI(model="gpt-4o", temperature=temperature)
    else:
        from langchain_ollama import ChatOllama
        model_name = os.getenv("OLLAMA_MODEL", "qwen2.5-coder:3b")
        return ChatOllama(model=model_name, temperature=temperature)


# Quick smoke test when running `python config.py` directly
if __name__ == "__main__":
    llm = get_llm()
    print(f"Testing LLM connection ({llm.model})...")
    response = llm.invoke("Reply with one short sentence: confirm you are online.")
    print("Response:", response.content)