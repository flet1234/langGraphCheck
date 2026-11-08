from pydantic import BaseModel, Field
from config import get_llm
from capstone.state import DevCycleState


class GeneratedFile(BaseModel):
    filepath: str = Field(description="Relative file path, e.g. 'src/validator.ts'")
    content: str = Field(description="Complete, valid TypeScript code for this file")


class GeneratedProject(BaseModel):
    files: list[GeneratedFile] = Field(description="List of TypeScript files to generate")


llm = get_llm()
structured_llm = llm.with_structured_output(GeneratedProject)


def implement_node(state: DevCycleState) -> dict:
    attempt = state.get("attempts", 0) + 1
    print(f"💻 [4. Implement] Generating TypeScript code (Attempt {attempt})...")

    retry_context = ""
    if state.get("code"):
        retry_context += f"\nPrevious code:\n{state['code']}\n"
    if state.get("test_output"):
        retry_context += f"\nPrevious TypeScript compiler errors to fix:\n{state['test_output']}\n"
    if state.get("feedback"):
        retry_context += f"\nHuman review feedback to address:\n{state['feedback']}\n"

    prompt = f"""You are a senior TypeScript engineer.
Rules:
- Write pure, standalone TypeScript functions/interfaces.
- Do NOT import Node.js modules (like 'assert', 'fs', 'path') or external npm libraries.
- Do NOT include ```typescript markdown fences inside the file content.
- Keep regular expressions on a single line.

Task: {state['task']}
Plan:
{state['plan']}
{retry_context}
Generate the TypeScript file(s) inside 'src/'."""

    result: GeneratedProject = structured_llm.invoke(prompt)  # type: ignore

    # Convert list[GeneratedFile] into dict[filepath, content]
    code_dict = {f.filepath: f.content for f in result.files}
    if not code_dict:
        code_dict = {"src/index.ts": "// Empty output fallback"}

    print(f"   📦 Generated files: {list(code_dict.keys())}")
    return {
        "code": code_dict,
        "attempts": attempt,
        "feedback": "",
    }