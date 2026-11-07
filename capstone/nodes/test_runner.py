import subprocess
from pathlib import Path
from capstone.state import DevCycleState


def test_runner_node(state: DevCycleState) -> dict:
    print("🧪 [5. Test Runner] Writing files & running TypeScript compiler check...")
    output_dir = Path(state["output_dir"])

    file_args: list[str] = []
    for filepath, content in state["code"].items():
        full_path = output_dir / filepath
        full_path.parent.mkdir(parents=True, exist_ok=True)
        full_path.write_text(content, encoding="utf-8")
        file_args.append(filepath)

    files_str = " ".join(file_args)
    tsc_result = subprocess.run(
        f"npx --yes -p typescript tsc {files_str} --noEmit --strict",
        cwd=output_dir,
        shell=True,
        capture_output=True,
        text=True,
        timeout=30,
    )

    tests_pass = tsc_result.returncode == 0
    output = (tsc_result.stdout + tsc_result.stderr).strip()

    if tests_pass:
        print("   ✅ TypeScript check PASSED (0 errors)!")
    else:
        print(f"   ❌ TypeScript check FAILED:\n{output}")

    return {"test_output": output, "tests_pass": tests_pass}