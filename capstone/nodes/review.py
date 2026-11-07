from langgraph.types import interrupt
from capstone.state import DevCycleState
from pathlib import Path
import shutil

def review_design_node(state: DevCycleState) -> dict:
    decision = interrupt({
        "stage": "design_review",
        "message": f"📋 Design is ready in {state['output_dir']}/design.md",
    })
    return {
        "approved": decision.get("approved", False),
        "feedback": decision.get("feedback", ""),
    }


def review_code_node(state: DevCycleState) -> dict:
    decision = interrupt({
        "stage": "code_review",
        "message": f"💻 Code is ready in {state['output_dir']}: {list(state['code'].keys())}",
        "tests_pass": state.get("tests_pass", False),
    })
    approved = decision.get("approved", False)
    # If rejected, clean up the rejected .ts files from output_dir!
    if not approved:
        shutil.rmtree(Path(state["output_dir"]) / "src", ignore_errors=True)
    return {
        "approved": approved,
        "feedback": decision.get("feedback", ""),
        "attempts": 0,
    }