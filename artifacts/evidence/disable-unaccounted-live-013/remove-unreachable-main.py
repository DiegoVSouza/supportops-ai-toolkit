from pathlib import Path

path = Path(__file__).resolve().parents[3] / "scripts/run_live_free_eval.py"
source = path.read_text(encoding="utf-8")
start = source.index("    # Historical direct execution retained below only until the entry point is removed.\n")
end = source.index('\nif __name__ == "__main__":', start)
path.write_text(source[:start] + source[end:], encoding="utf-8", newline="\n")
