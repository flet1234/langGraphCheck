from typing import TypedDict
from langgraph.graph import StateGraph, START, END
from config import get_llm

llm = get_llm()


# 1. Define State — the shared data object (like a TS interface)
class State(TypedDict):
    topic: str
    summary: str
    translation: str

class InputState(TypedDict):
    topic:str

# 2. Define a Node — takes State, returns a dict of updates
def summarize(state: State) -> dict:
    print(f"--- [Node: summarize] working on: {state['topic']} ---")
    prompt = f"Write one short paragraph about: {state['topic']}"
    result = llm.invoke(prompt)
    return {"summary": result.content}

def translate(state:State) -> dict:
    print("Translation Node")
    prompt = f"Translate all text from {state['summary']} to Russian language"
    result = llm.invoke(prompt)
    return {"translation": result.content}

# 3. Build the Graph
graph = StateGraph(State, input_schema=InputState)
graph.add_node("summarize", summarize)
graph.add_node("translation", translate)

graph.add_edge(START, "summarize")
graph.add_edge("summarize", "translation")
graph.add_edge("translation", END)

# Compile turns the graph definition into an executable runnable
app = graph.compile()


# 4. Run it!
if __name__ == "__main__":
    result = app.invoke({"topic": "LangGraph for agentic workflows"})
    print("\nFinal State:")
    print(f"Summary: {result['summary']}\nTranslation: {result['translation']}")