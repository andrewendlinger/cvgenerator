import subprocess
from pathlib import Path

import pytest
import toml

# Define paths relative to the project root
CONFIG_PATH = Path("app/config.toml")
OUTPUT_DIR = Path("output")


@pytest.fixture
def override_config():
    """A pytest fixture to safely overwrite and restore the main config.toml."""
    original_content = None
    if CONFIG_PATH.exists():
        original_content = CONFIG_PATH.read_text(encoding="utf-8")
    yield
    if original_content:
        CONFIG_PATH.write_text(original_content, encoding="utf-8")
    elif CONFIG_PATH.exists():
        CONFIG_PATH.unlink()


# --- Configuration for our two test cases ---

# Case 1: Fast local build that generates a .tex file
local_tex_config = {
    "build_settings": {"use_docker": False},
    "output_settings": {
        "output_format": "tex",
        "cleanup_temp_files": False,
        "output_mode": "dump",
    },
}

# Case 2: Slow Docker build that generates a .pdf file
docker_pdf_config = {
    "build_settings": {"use_docker": True},
    "output_settings": {
        "output_format": "pdf",
        "cleanup_temp_files": True,
        "output_mode": "dump",
    },
}


@pytest.mark.parametrize(
    "test_id, build_config, expected_extension",
    [
        pytest.param("local_tex", local_tex_config, ".tex", id="fast_local_tex_build"),
        pytest.param(
            "docker_pdf",
            docker_pdf_config,
            ".pdf",
            marks=pytest.mark.slow,
            id="slow_docker_pdf_build",
        ),
    ],
)
def test_build_process(override_config, test_id, build_config, expected_extension):
    """A single, parameterized test for different build configurations."""
    test_base_filename = f"pytest_{test_id}"
    expected_file_path = OUTPUT_DIR / f"{test_base_filename}{expected_extension}"

    test_config = {
        "cv_settings": {
            "facet_to_generate": "academia",
            "content_file": "./content/mariecurie_cv.toml",
            "template_file": "./templates/cv_template.tex.j2",
        },
        **build_config,
    }
    test_config["output_settings"]["base_filename"] = test_base_filename

    OUTPUT_DIR.mkdir(exist_ok=True)
    try:
        CONFIG_PATH.write_text(toml.dumps(test_config), encoding="utf-8")

        # MODIFICATION: Removed 'capture_output=True' and 'text=True'
        # This allows the command's output to stream directly to the terminal.
        subprocess.run(
            ["uv", "run", "task", "build"],
            check=True,
            encoding="utf-8",
        )

        assert expected_file_path.exists(), f"File not found: {expected_file_path}"
    finally:
        if expected_file_path.exists():
            # This print statement from the test itself will still be visible
            print(f"\nCleaned up test file: {expected_file_path}")
            expected_file_path.unlink()
