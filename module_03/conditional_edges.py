from typing import TypedDict
from langgraph.graph import StateGraph, START, END
from config import get_llm

llm = get_llm(temperature=0.7)  # higher temperature so retries generate different passwords!


class InputState(TypedDict):
    pass  # Or you can pass {"max_attempts": int}


class State(TypedDict):
    password: str
    is_strong: bool
    attempts: int
    
def generate_password(state:State) -> dict:
    prompt = "Output a single random password. Do NOT include any explanation, markdown, backticks, or spaces. Output ONLY the raw password."
    response = llm.invoke(prompt)
    return {"password": response.text.strip(), "attempts": state.get("attempts", 0) + 1}

def check_strength(state:State) -> dict:
    pwd = state['password']
    if(
        len(pwd) >= 12
        and not any(c.isspace() for c in pwd)
        and any(c.isdigit() for c in pwd)
        and any(c.isupper() for c in pwd)
    ):
        print(f"Attempt: {state['attempts']} is passed")
        return {"is_strong":True}
    else:
       print(f"Attempt: {state['attempts']} is not passed")
    return {"is_strong":False}

def router(state:State) -> str:
    if state["is_strong"]: return "done"
    elif state["attempts"] >= 3:return  "max_retries"
    else: return "retry"
    
graph = StateGraph(State, input_schema=InputState)
graph.add_node("generate", generate_password)    
graph.add_node("strength", check_strength)    

graph.add_edge(START, 'generate') 
graph.add_edge("generate", 'strength')
graph.add_conditional_edges("strength", router, {"done":END, "max_retries": END, "retry": "generate"})

app = graph.compile()

if __name__ == "__main__":
    result=app.invoke({})
    print(f"Final State: {result['password']} with {result['attempts']} attempts")