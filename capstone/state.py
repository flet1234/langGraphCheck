from typing import TypedDict


class InputState(TypedDict):
    task: str
    output_dir: str
    max_attempts: int


class DevCycleState(TypedDict):
    # Input
    task: str
    output_dir: str
    max_attempts: int

    # Artifacts (created as the ticket moves through the pipeline)
    research: str
    design: str
    plan: str
    code: dict[str, str]  # e.g. {"src/validator.ts": "export function ..."}
    test_output: str

    # Control flags
    attempts: int
    approved: bool
    feedback: str
    tests_pass: bool