import uuid
from langchain_core.runnables import RunnableConfig
from langgraph.types import Command
from langgraph.checkpoint.sqlite import SqliteSaver
from capstone.graph import build_graph


def run_pipeline(task: str, output_dir: str = "output/capstone_project"):
    with SqliteSaver.from_conn_string("output/pipeline.db") as checkpointer:
        app = build_graph().compile(checkpointer=checkpointer)
        thread_id = str(uuid.uuid4())
        config: RunnableConfig = {"configurable": {"thread_id": thread_id}}

        print(f"🚀 Starting Capstone Pipeline | thread_id: {thread_id}")
        print(f"📁 Output directory: {output_dir}")

        # 1. Start the pipeline (runs until the first interrupt: review_design)
        app.invoke(
            {"task": task, "output_dir": output_dir, "max_attempts": 3},
            config=config,
        )

        # 2. Loop while the graph is paused at any human review checkpoint
        while True:
            state = app.get_state(config)
            if state.next:
                interrupt_info = state.tasks[0].interrupts[0].value
                print(f"\n⏸️  PAUSED at node: {state.next[0]}")
                print(f"   {interrupt_info.get('message', '')}")

                ans = input("👉 Approve? (y/n): ").strip().lower()
                notes = ""
                if ans != "y":
                    notes = input("📝 Enter feedback for revision: ").strip()

                app.invoke(
                    Command(resume={"approved": ans == "y", "feedback": notes}),
                    config=config,
                )
            else:
                print(f"\n🎉 Pipeline complete! Final files are in: {output_dir}")
                break


if __name__ == "__main__":
    run_pipeline("A TypeScript utility that validates email addresses and strong passwords")