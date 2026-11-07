from pathlib import Path
from config import get_llm
from capstone.state import DevCycleState

llm = get_llm()


def plan_node(state: DevCycleState) -> dict:
    print("📋 [3. Plan] Creating plan.md...")
    prompt = f"""You are a tech lead creating an implementation plan.

Task: {state['task']}
Design:
{state['design']}

Write a concise plan.md:
# Implementation Plan
## Files to Create
## Step-by-Step Implementation"""

    result = llm.invoke(prompt)
    plan = result.text.strip()

    out_dir = Path(state["output_dir"])
    (out_dir / "plan.md").write_text(plan, encoding="utf-8")
    print(f"   💾 Saved {out_dir / 'plan.md'}")

    return {"plan": plan, "feedback": ""}