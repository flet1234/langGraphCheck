from config import get_llm
from capstone.state import DevCycleState

llm = get_llm()


def research_node(state: DevCycleState) -> dict:
    print(f"\n🔍 [1. Research] Researching: {state['task']}")
    prompt = f"""You are a senior engineer doing technical research.

Task to build: {state['task']}

Research and document briefly:
1. Best approach / architecture
2. Key TypeScript patterns to use
3. Potential edge cases and how to avoid them"""

    result = llm.invoke(prompt)
    return {"research": result.text.strip()}