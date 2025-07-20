# app/main.py
"""
Main entry point for the CV Generation script.

This script orchestrates the full lifecycle of building a LaTeX CV from a
Jinja2 template and TOML content file. It handles configuration loading,
output directory setup, template rendering, LaTeX compilation, and cleanup.

To run the script from the project root:
    $ python app/main.py
    or
    $ uv run task build
"""

import os
import subprocess
import sys
import traceback
from datetime import datetime
from pathlib import Path

import toml

# --- Global Path Constants ---
APP_DIR = Path(__file__).resolve().parent
PROJECT_ROOT = APP_DIR.parent
CONFIG_FILE = APP_DIR / "config.toml"

# --- Dynamic Script Imports ---
sys.path.append(str(APP_DIR))
from scripts.assets import copy_assets_to_output, remove_assets  # noqa: E402
from scripts.clean_tex import clean_auxiliary_tex_files  # noqa: E402
from scripts.generate_tex import generate  # noqa: E402


def load_config():
    """Load the TOML configuration file."""
    return toml.load(CONFIG_FILE)


def is_inside_docker():
    """Check if the script is currently running inside a Docker container."""
    return os.environ.get("INSIDE_DOCKER") is not None


def build_and_run_in_docker():
    """Build the Docker image and re-run the script inside a new container."""
    print(
        "🐳 Docker mode is enabled. Building image and running script inside a container..."
    )

    command = (
        f"docker build -t latex-cv . && "
        f'docker run --rm -v "{PROJECT_ROOT}:/work" -w /work -e INSIDE_DOCKER=true latex-cv python app/main.py && '
        f"docker image prune -f > /dev/null"
    )

    try:
        subprocess.run(command, shell=True, check=True, cwd=PROJECT_ROOT)
    except FileNotFoundError:
        print("❌ Error: 'docker' command not found. Is Docker installed?")
        sys.exit(1)
    except subprocess.CalledProcessError as e:
        print(f"❌ Docker execution failed with code {e.returncode}: {e}")
        sys.exit(1)


def compile_pdf(tex_path: Path, output_dir: Path):
    """Compile the .tex file into a PDF using pdflatex."""
    print("\n📄 Compiling PDF with pdflatex...")
    try:
        subprocess.run(
            ["pdflatex", "-interaction=nonstopmode", tex_path.name],
            cwd=output_dir,
            capture_output=True,
            text=True,
            check=True,
        )
    except subprocess.CalledProcessError as e:
        print("❌ Error during PDF compilation. See log below:")
        print("-" * 60)
        print(e.stdout)
        print(e.stderr)
        print("-" * 60)
        print(f"ℹ️  Check the log file: {tex_path.with_suffix('.log')}")
        sys.exit(1)


def main():
    """Main orchestration of the CV generation process."""
    print("🚀 Starting CV generation...\n")

    config = load_config()

    try:
        settings_cv = config["cv_settings"]
        settings_output = config["output_settings"]

        facet = settings_cv["facet_to_generate"]
        cleanup = settings_output["cleanup_temp_files"]
        output_mode = settings_output["output_mode"]
        output_format = settings_output["output_format"]
        output_cv_filename = settings_output["base_filename"]
    except KeyError as e:
        print(
            f"❌ Faulty config.toml - missing key: {e}\n\n{traceback.format_exc(chain=False)}"
        )
        sys.exit(1)

    # Determine output directory
    if output_mode == "auto":
        timestamp = datetime.now().strftime("%d%b%Y_%H%M%S")
        output_dir_name = f"{timestamp}_cv_{facet}"
    elif output_mode == "dump":
        output_dir_name = "."
    else:
        print("❌ Invalid 'output_mode' in config. Use 'auto' or 'dump'.")
        sys.exit(1)

    final_output_dir = PROJECT_ROOT / "output" / output_dir_name
    final_output_dir.mkdir(parents=True, exist_ok=True)
    print(f"📁 Created output directory: {final_output_dir.relative_to(PROJECT_ROOT)}")

    output_tex_path = final_output_dir / Path(output_cv_filename).with_suffix(".tex")

    # Generate the .tex file from Jinja2 template
    try:
        generate(CONFIG_FILE, output_tex_path)
    except Exception as e:
        print(
            f"❌ Error during TeX generation: {e}\n\n{traceback.format_exc(chain=False)}"
        )
        sys.exit(1)

    if output_format.lower() == "tex":
        print(
            f"\n✅ CV generation complete! LaTeX file saved at: {output_tex_path.relative_to(PROJECT_ROOT)}"
        )
        return
    elif output_format.lower() != "pdf":
        print("❌ Invalid 'output_format' in config. Use 'tex' or 'pdf'.")
        sys.exit(1)

    # Copy assets and compile
    copy_assets_to_output(final_output_dir)
    print("➡️  Assets copied to output folder")

    compile_pdf(output_tex_path, final_output_dir)

    # Optional cleanup
    if cleanup:
        remove_assets(final_output_dir)
        clean_auxiliary_tex_files(str(final_output_dir))
        print("\n🧹 Temporary LaTeX files and assets cleaned up.")

    print(
        f"\n✅ CV generation complete! PDF saved at: {output_tex_path.with_suffix('.pdf').relative_to(PROJECT_ROOT)}"
    )


def main_entry():
    """Entry point with Docker integration."""
    config = load_config()
    use_docker = config.get("build_settings", {}).get("use_docker", False)

    if use_docker and not is_inside_docker():
        build_and_run_in_docker()
    else:
        if is_inside_docker():
            print("\n--- Script running inside Docker container ---\n")
        main()


if __name__ == "__main__":
    main_entry()
