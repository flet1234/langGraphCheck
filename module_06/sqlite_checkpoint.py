from typing import TypedDict
from langchain_core.runnables import RunnableConfig
from langgraph.graph import StateGraph, START, END
from langgraph.checkpoint.sqlite import SqliteSaver
from langgraph.types import interrupt, Command
from config import get_llm

llm = get_llm()


class InputState(TypedDict):
    topic: str


class State(TypedDict):
    topic: str
    draft: str
    approved: bool
    final_post: str


def write_draft(state: State) -> dict:
    print(f"--- [Node: write_draft] Writing draft about: {state['topic']} ---")
    res = llm.invoke(f"Write a 2-sentence LinkedIn post about: {state['topic']}")
    return {"draft": res.text.strip()}


def human_review(state: State) -> dict:
    # Pause here!
    approved = interrupt(f"Review this draft:\n{state['draft']}\nApprove? (y/n)")
    print(f"--- [Node: human_review] Resumed! Approved = {approved} ---")
    return {"approved": approved}


def publish(state: State) -> dict:
    if state["approved"]:
        print("--- [Node: publish] Publishing post! ---")
        return {"final_post": f"PUBLISHED: {state['draft']}"}
    else:
        print("--- [Node: publish] Post rejected. ---")
        return {"final_post": "REJECTED"}


graph = StateGraph(State, input_schema=InputState)
graph.add_node("write_draft", write_draft)
graph.add_node("human_review", human_review)
graph.add_node("publish", publish)

graph.add_edge(START, "write_draft")
graph.add_edge("write_draft", "human_review")
graph.add_edge("human_review", "publish")
graph.add_edge("publish", END)


if __name__ == "__main__":
    config: RunnableConfig = {"configurable": {"thread_id": "persistent-run-1"}}

    with SqliteSaver.from_conn_string("output/checkpoints.db") as checkpointer:
        app = graph.compile(checkpointer=checkpointer)

        # Check what's already saved in SQLite for "persistent-run-1"!
        saved_state = app.get_state(config)

        if not saved_state.values:
            # RUN 1: Nothing in DB yet -> start the graph!
            print("🚀 [RUN 1] Starting fresh run...")
            app.invoke({"topic": "Why local LLMs with Ollama are great"}, config=config)
            print("\n⏸️  Graph paused and saved to output/checkpoints.db!")
            print("👉 Now run this exact same command AGAIN to resume from SQLite!")

        elif saved_state.next:
            # RUN 2: Found a paused graph in SQLite from a previous process!
            print(f"🔄 [RUN 2] Found paused graph in SQLite at node: {saved_state.next}")
            print(f"Saved draft from previous run:\n  \"{saved_state.values['draft']}\"\n")

            ans = input("Approve this draft? (y/n): ").strip().lower()
            result = app.invoke(Command(resume=(ans == "y")), config=config)
            print(f"\nFinal Result: {result['final_post']}")

        else:
            # RUN 3+: Graph already finished in the past! Show history:
            print("✅ This thread_id already completed! Here is its checkpoint history:")
            for step in app.get_state_history(config):
                print(f" - step={step.metadata.get('step') if step.metadata else None} | keys={list(step.values.keys())}")