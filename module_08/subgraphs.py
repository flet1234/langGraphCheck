from typing import TypedDict
from langgraph.graph import StateGraph, START, END
from config import get_llm

llm = get_llm()


# ==========================================
# 1. SUBGRAPH A: Researcher Agent
# ==========================================
class ResearchState(TypedDict):
    topic: str
    raw_ideas: str
    findings: str


def gather_tech(state: ResearchState) -> dict:
    print("🔍 [Subgraph: Researcher] Step 1: Gathering tech stack ideas...")
    res = llm.invoke(f"List 3 key libraries/technologies for: {state['topic']}")
    return {"raw_ideas": res.text.strip()}


def summarize_research(state: ResearchState) -> dict:
    print("🔍 [Subgraph: Researcher] Step 2: Summarizing research...")
    res = llm.invoke(f"Turn these tech notes into a 2-sentence recommendation:\n{state['raw_ideas']}")
    return {"findings": res.text.strip()}


research_builder = StateGraph(ResearchState)
research_builder.add_node("gather_tech", gather_tech)
research_builder.add_node("summarize_research", summarize_research)
research_builder.add_edge(START, "gather_tech")
research_builder.add_edge("gather_tech", "summarize_research")
research_builder.add_edge("summarize_research", END)

researcher_subgraph = research_builder.compile()


# ==========================================
# 2. SUBGRAPH B: Security Agent
# ==========================================
class SecurityState(TypedDict):
    topic: str
    risks: str
    security_report: str


def find_risks(state: SecurityState) -> dict:
    print("🛡️  [Subgraph: Security] Step 1: Identifying security risks...")
    res = llm.invoke(f"List 2 top security risks when building: {state['topic']}")
    return {"risks": res.text.strip()}


def propose_mitigations(state: SecurityState) -> dict:
    print("🛡️  [Subgraph: Security] Step 2: Proposing mitigations...")
    res = llm.invoke(f"Give 1-sentence fixes for each of these risks:\n{state['risks']}")
    return {"security_report": res.text.strip()}


security_builder = StateGraph(SecurityState)
security_builder.add_node("find_risks", find_risks)
security_builder.add_node("propose_mitigations", propose_mitigations)
security_builder.add_edge(START, "find_risks")
security_builder.add_edge("find_risks", "propose_mitigations")
security_builder.add_edge("propose_mitigations", END)

security_subgraph = security_builder.compile()


# ==========================================
# 3. PARENT GRAPH: Orchestrator
# ==========================================
class InputState(TypedDict):
    task: str


class MainState(TypedDict):
    task: str
    research_output: str
    security_output: str
    final_proposal: str


def run_research_agent(state: MainState) -> dict:
    # Call Subgraph A with its own state schema!
    result = researcher_subgraph.invoke({"topic": state["task"]})  # type: ignore
    return {"research_output": result["findings"]}


def run_security_agent(state: MainState) -> dict:
    # Call Subgraph B with its own state schema!
    result = security_subgraph.invoke({"topic": state["task"]})  # type: ignore
    return {"security_output": result["security_report"]}


def synthesize(state: MainState) -> dict:
    print("\n🧠 [Parent: synthesize] Combining Research + Security reports...")
    prompt = f"""Combine these two agent reports into a short Architecture Summary for '{state['task']}':

Tech Research:
{state['research_output']}

Security Review:
{state['security_output']}"""
    res = llm.invoke(prompt)
    return {"final_proposal": res.text.strip()}


main_builder = StateGraph(MainState, input_schema=InputState)
main_builder.add_node("research_agent", run_research_agent)
main_builder.add_node("security_agent", run_security_agent)
main_builder.add_node("synthesize", synthesize)

# FAN-OUT: Both agents start in PARALLEL from START!
main_builder.add_edge(START, "research_agent")
main_builder.add_edge(START, "security_agent")

# FAN-IN: Wait for both to finish, then run synthesize!
main_builder.add_edge("research_agent", "synthesize")
main_builder.add_edge("security_agent", "synthesize")
main_builder.add_edge("synthesize", END)

app = main_builder.compile()


if __name__ == "__main__":
    result = app.invoke({"task": "A user authentication API in TypeScript with JWT"})
    print("\n================ FINAL PROPOSAL ================")
    print(result["final_proposal"])