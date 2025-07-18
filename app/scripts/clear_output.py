import shutil
from pathlib import Path


def clear_output_dir():
    """
    Deletes all files and folders inside the 'output/' directory,
    located relative to this script file (app/scripts/clean.py),
    but does not delete the 'output/' directory itself.
    """
    # Locate 'output' directory relative to this script's parent directory (app/)
    output_dir = Path(__file__).resolve().parent.parent.parent / "output"

    if not output_dir.exists() or not output_dir.is_dir():
        print(f"❌  No output directory found at {output_dir}")
        return

    for item in output_dir.iterdir():
        try:
            if item.is_dir():
                if item.name != "demo":
                    shutil.rmtree(item)
            else:
                item.unlink()
        except Exception as e:
            print(f"❌  Failed to delete {item}: {e}")
            return

    print("🗑️  Removed all files from the output directory.")


if __name__ == "__main__":
    clear_output_dir()
