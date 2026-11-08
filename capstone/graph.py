from langgraph.graph import StateGraph, START, END
from capstone.state import DevCycleState, InputState
from capstone.nodes.research import research_node
from capstone.nodes.design import design_node
from capstone.nodes.plan import plan_node
from capstone.nodes.implement import implement_node
from capstone.nodes.test_runner import test_runner_node
from capstone.nodes.review import review_design_node, review_code_node


def route_after_design_review(state: DevCycleState) -> str:
    return "plan" if state["approved"] else "design"


def route_after_tests(state: DevCycleState) -> str:
    if state["tests_pass"]:
        return "review_code"
    if state.get("attempts", 0) >= state.get("max_attempts", 3):
        return "review_code"  # let human inspect even if failing after max tries
    return "implement"


def route_after_code_review(state: DevCycleState) -> str:
    return "done" if state["approved"] else "implement"


def build_graph():
    graph = StateGraph(DevCycleState, input_schema=InputState)

    graph.add_node("research", research_node)
    graph.add_node("design", design_node)
    graph.add_node("review_design", review_design_node)
    graph.add_node("plan", plan_node)
    graph.add_node("implement", implement_node)
    graph.add_node("run_tests", test_runner_node)
    graph.add_node("review_code", review_code_node)

    graph.add_edge(START, "research")
    graph.add_edge("research", "design")
    graph.add_edge("design", "review_design")
    graph.add_conditional_edges("review_design", route_after_design_review, {
        "plan": "plan",
        "design": "design",
    })
    graph.add_edge("plan", "implement")
    graph.add_edge("implement", "run_tests")
    graph.add_conditional_edges("run_tests", route_after_tests, {
        "review_code": "review_code",
        "implement": "implement",
    })
    graph.add_conditional_edges("review_code", route_after_code_review, {
        "done": END,
        "implement": "implement",
    })

    return graph