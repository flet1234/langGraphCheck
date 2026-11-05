import subprocess
from pathlib import Path
from typing import TypedDict, Annotated
from langchain_core.tools import tool
from langchain_core.messages import AnyMessage, HumanMessage, SystemMessage
from langgraph.graph import StateGraph, START, END
from langgraph.graph.message import add_messages
from langgraph.prebuilt import ToolNode, tools_condition
from config import get_llm
import re
import json


# 1. Define Tools with @tool (Type hints + Docstring are required!)
@tool
def read_file(path: str) -> str:
    """Read a file from disk given its relative path."""
    print(f"🔧 [Tool: read_file] Reading {path}")
    return Path(path).read_text(encoding="utf-8")


@tool
def write_file(path: str, content: str) -> str:
    """Write text content to a file on disk."""
    print(f"🔧 [Tool: write_file] Writing to {path}")
    p = Path(path)
    p.parent.mkdir(parents=True, exist_ok=True)
    p.write_text(content, encoding="utf-8")
    return f"Successfully wrote to {path}"


@tool
def check_ts_file(path: str) -> str:
    """Run TypeScript compiler (npx tsc) on a .ts file to check for type errors."""
    print(f"🔧 [Tool: check_ts_file] Checking types in {path}")
    result = subprocess.run(
        f"npx --yes -p typescript tsc {path} --noEmit --strict",
        shell=True,
        capture_output=True,
        text=True,
        timeout=30,
    )
    if result.returncode == 0:
        return "SUCCESS: No TypeScript errors!"
    return f"TYPESCRIPT ERRORS:\n{result.stdout + result.stderr}"


tools = [read_file, write_file, check_ts_file]

# 2. Bind tools to the LLM
llm = get_llm()
llm_with_tools = llm.bind_tools(tools)


# 3. State uses `add_messages` reducer so every message (Human, AI, Tool) appends!
class State(TypedDict):
    messages: Annotated[list[AnyMessage], add_messages]


def agent_node(state: State) -> dict:
    print("\n🤖 [Node: agent] Thinking...")
    response = llm_with_tools.invoke(state["messages"])
    return {"messages": [response]}


# 4. Build the ReAct Graph
graph = StateGraph(State)
graph.add_node("agent", agent_node)
graph.add_node("tools", ToolNode(tools))

graph.add_edge(START, "agent")
graph.add_conditional_edges("agent", tools_condition)  # routes to "tools" or END
graph.add_edge("tools", "agent")  # after running a tool, go back to agent!

app = graph.compile()


if __name__ == "__main__":
    # Create the buggy TypeScript file first so the agent has something to read
    Path("output").mkdir(exist_ok=True)
    Path("output/buggy.ts").write_text(
        'export function add(a: number, b: number): number {\n'
        '    const broken: number = "hello";\n'
        '    return a + b;\n'
        '}\n',
        encoding="utf-8",
    )

    prompt = (
        "1. Read 'output/buggy.ts' using read_file.\n"
        "2. Fix the TypeScript type error and write the fixed code to 'output/fixed.ts' using write_file.\n"
        "3. Run check_ts_file on 'output/fixed.ts' to verify there are no errors."
    )

    result = app.invoke({
        "messages": [
            SystemMessage(content="You are a coding assistant. Always use the provided tools step by step."),
            HumanMessage(content=prompt),
        ]
    })

    print("\n✅ Final Agent Response:")
    print(result["messages"][-1].text)