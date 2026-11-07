from pathlib import Path
from config import get_llm
from capstone.state import DevCycleState

llm = get_llm()


def design_node(state: DevCycleState) -> dict:
    print("📐 [2. Design] Creating design.md...")
    feedback_section = ""
    if state.get("feedback"):
        feedback_section = f"\nHuman feedback to address:\n{state['feedback']}\n"

    prompt = f"""You are a software architect.

Task: {state['task']}
Research findings:
{state['research']}
{feedback_section}
Write a concise design.md in Markdown covering:
# Design
## Architecture
## Key TypeScript Types/Interfaces
## File Structure (keep it to 1-2 files inside src/)
## Edge Cases"""

    result = llm.invoke(prompt)
    design = result.text.strip()

    out_dir = Path(state["output_dir"])
    out_dir.mkdir(parents=True, exist_ok=True)
    (out_dir / "design.md").write_text(design, encoding="utf-8")
    print(f"   💾 Saved {out_dir / 'design.md'}")

    return {"design": design}