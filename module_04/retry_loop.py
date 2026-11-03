import re
import sys
import subprocess
from pathlib import Path
from typing import TypedDict
from langgraph.graph import StateGraph, START, END
from config import get_llm

llm = get_llm()


class InputState(TypedDict):
    task: str
    max_attempts: int


class State(TypedDict):
    task: str
    code: str
    test_output: str
    tests_pass: bool
    attempts: int
    max_attempts: int


def implement(state: State) -> dict:
    attempt = state.get("attempts", 0) + 1
    print(f"\n--- [Node: implement] Attempt {attempt} ---")

    prompt = f"""Write Python code for: {state['task']}

Previous test failure (if any):
{state.get('test_output', 'None - first attempt')}

Return ONLY valid Python code, no markdown fences or explanations."""

    result = llm.invoke(prompt)
    # Strip ```python ... ``` if the local 3B model adds markdown fences anyway
    clean_code = re.sub(r"^```(?:python)?\s*|\s*```$", "", result.text.strip(), flags=re.MULTILINE).strip()

    return {
        "code": clean_code,
        "attempts": attempt,
    }


def run_tests(state: State) -> dict:
    print("--- [Node: run_tests] Running pytest ---")
    output_dir = Path("output")
    output_dir.mkdir(exist_ok=True)

    # 1. Write the LLM's generated code to output/solution.py
    (output_dir / "solution.py").write_text(state["code"], encoding="utf-8")

    # 2. Run pytest on output/test_solution.py
    result = subprocess.run(
        [sys.executable, "-m", "pytest", "module_04/test_solution.py", "-q"],
        capture_output=True,
        text=True,
        timeout=10,
    )

    passed = result.returncode == 0
    output_log = result.stdout + result.stderr
    print(f"Tests passed: {passed}")
    if not passed:
        print(f"Failure output:\n{output_log}")

    return {
        "test_output": output_log,
        "tests_pass": passed,
    }
    
def router(state:State) -> str:
    if state["tests_pass"] == True: return "END"
    if state["attempts"] >= 3: return "END"
    else: return "retry"
    
graph = StateGraph(State, input_schema=InputState)
graph.add_node("implement", implement)
graph.add_node("run_tests", run_tests)

graph.add_edge(START, "implement")
graph.add_edge("implement", "run_tests")
graph.add_conditional_edges("run_tests", router, {"END":END, "retry":"implement"})

app=graph.compile()

if __name__ == "__main__":
    result = app.invoke({
    "task": "Write a function `fibonacci(n: int) -> int`",
    "max_attempts": 3,
})