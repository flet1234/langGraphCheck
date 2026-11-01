from typing import TypedDict
from langgraph.graph import StateGraph, START, END
from config import get_llm
from pathlib import Path

llm = get_llm()

class State(TypedDict):
    input: str
    output: str
    valid: bool
    file_written:bool
    
class InputState(TypedDict):
    input:str
    
def validate (state:State) -> dict:
    cleaned_input = state["input"].strip()
    is_valid = len(cleaned_input)>0
    
    print()
    return {
        "input": cleaned_input,
        "valid": is_valid,
    }
    
def generate (state:State) -> dict:
    if state['valid']:
        result = llm.invoke(state["input"])
        return {"output": result.content}
    else:   
        return {"output": "Error: input was empty"}
    
def save (state:State) -> dict:
    Path("output").mkdir(exist_ok=True)
    Path("output/result.txt").write_text(state['output'], encoding="utf-8")
    return {"file_written":True}
    
graph = StateGraph(State, input_schema=InputState)

graph.add_node("validate", validate)
graph.add_node("generate", generate)
graph.add_node("save", save)

graph.add_edge(START, "validate")
graph.add_edge("validate", "generate")
graph.add_edge("generate", "save")
graph.add_edge("save", END)

app = graph.compile()

if __name__ == "__main__":
    result = app.invoke({"input": "   "})
    print(f'Final state : {result['file_written']}')
    
