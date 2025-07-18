import shutil
from pathlib import Path

source_assets_dir = Path(__file__).resolve().parent.parent / "assets"


def copy_assets_to_output(output_dir: str):
    """
    Copies the entire assets folder into the LaTeX output folder temporarily.

    Args:
        source_assets_dir (str): Path to the original assets folder (e.g., 'app/assets')
        output_dir (str): Path to the LaTeX output folder (e.g., 'output/17Jul2025_144521_cv_academic')
    Returns:
        Path: Path to the new temporary assets folder inside the output directory
    """
    source = Path(source_assets_dir)
    destination = Path(output_dir) / "assets"

    if not source.exists() or not source.is_dir():
        raise FileNotFoundError(f"❌  Source assets folder not found: {source}")

    # Ensure the destination exists and copy
    if destination.exists():
        shutil.rmtree(destination)
    shutil.copytree(source, destination)

    return destination


def remove_assets(output_dir: str):
    destination = Path(output_dir) / "assets"

    if destination.exists():
        shutil.rmtree(destination)
