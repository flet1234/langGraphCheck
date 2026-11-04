import re
import sys
import subprocess
from pathlib import Path
from typing import TypedDict
from langgraph.graph import StateGraph, START, END
from langgraph.checkpoint.memory import MemorySaver
from langgraph.types import interrupt, Command
from langchain_core.runnables import RunnableConfig
from config import get_llm

llm = get_llm()


class InputState(TypedDict):
    task: str


class State(TypedDict):
    task: str
    code: str
    test_output: str
    tests_pass: bool
    attempts: int
    stop_requested: bool


def implement(state: State) -> dict:
    attempt = state.get("attempts", 0) + 1
    print(f"\n--- [Node: implement] Attempt {attempt} | Task: {state['task']} ---")

    prompt = f"""Write Python code for: {state['task']}

Previous code:
{state.get('code', 'None')}

Previous test failure:
{state.get('test_output', 'None')}

Return ONLY valid Python code, no markdown fences."""

    result = llm.invoke(prompt)
    clean_code = re.sub(r"^```(?:python)?\s*|\s*```$", "", result.text.strip(), flags=re.MULTILINE).strip()
    return {"code": clean_code, "attempts": attempt}


def run_tests(state: State) -> dict:
    print("--- [Node: run_tests] Running pytest ---")
    Path("output").mkdir(exist_ok=True)
    Path("output/solution.py").write_text(state["code"], encoding="utf-8")

    result = subprocess.run(
        [sys.executable, "-m", "pytest", "module_04/test_solution.py", "-q"],
        capture_output=True,
        text=True,
        timeout=10,
    )
    passed = result.returncode == 0
    print(f"Tests passed: {passed}")
    return {"test_output": result.stdout + result.stderr, "tests_pass": passed}


def human_help(state: State) -> dict:
    print("\n⏸️  [Node: human_help] Pausing for human input...")
    # Pause the graph and send info to the caller
    decision = interrupt({
        "message": f"Failed {state['attempts']} times!",
        "last_error": state["test_output"],
    })

    # When resumed, `decision` holds what the human answered
    if decision.get("stop"):
        return {"stop_requested": True}

    new_task = decision.get("new_task") or state["task"]
    return {
        "task": new_task,
        "attempts": 0,  # reset counter so it can try again!
        "stop_requested": False,
    }


def route_after_tests(state: State) -> str:
    if state["tests_pass"]:
        return "done"
    if state["attempts"] >= 2:
        return "ask_human"
    return "retry"


def route_after_human(state: State) -> str:
    if state.get("stop_requested"):
        return "give_up"
    return "retry"


graph = StateGraph(State, input_schema=InputState)
graph.add_node("implement", implement)
graph.add_node("run_tests", run_tests)
graph.add_node("human_help", human_help)

graph.add_edge(START, "implement")
graph.add_edge("implement", "run_tests")
graph.add_conditional_edges("run_tests", route_after_tests, {
    "done": END,
    "retry": "implement",
    "ask_human": "human_help",
})
graph.add_conditional_edges("human_help", route_after_human, {
    "retry": "implement",
    "give_up": END,
})

# MUST compile with a checkpointer to use interrupt()!
checkpointer = MemorySaver()
app = graph.compile(checkpointer=checkpointer)


if __name__ == "__main__":
    config: RunnableConfig  = {"configurable": {"thread_id": "session-1"}}

    # 1. Start with a bad task name (`fib` instead of `fibonacci`) so it fails twice!
    app.invoke({"task": "Write a function `fib(n)` that returns 0 always."}, config=config)

    # 2. Check if the graph is paused at an interrupt
    current_state = app.get_state(config)
    if current_state.next:
        print(f"\nGraph is PAUSED before completing: {current_state.next}")
        choice = input("Keep trying with better task? (y/n): ").strip().lower()

        if choice == "y":
            better_task = "Write `fibonacci(n: int) -> int` where fibonacci(0)=0, fibonacci(1)=1, and for n<0 return -1."
            # 3. Resume the paused graph!
            app.invoke(Command(resume={"stop": False, "new_task": better_task}), config=config)
        else:
            app.invoke(Command(resume={"stop": True}), config=config)