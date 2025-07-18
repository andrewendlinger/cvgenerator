# AI Assistant Context: CV Generator Project

This document provides a comprehensive overview of the CV Generator project. Its purpose is to give you, the AI assistant, all the necessary context to understand, debug, and extend the project's functionality.

---

## 1. Project Overview & Goal 🎯

The project is a Python-based tool designed to **generate professional PDF and LaTeX CVs from a single structured data file**.

The core philosophy is the **separation of content from presentation**.
* **Content**: All personal data, experience, education, skills, etc., are stored in a simple, human-readable `TOML` file.
* **Presentation**: The visual layout, styling, and structure of the CV are defined in `Jinja2` templates that produce `LaTeX` code.

A key feature is the **"facet" system**, which allows the user to generate different versions of a CV (e.g., one for academia, one for industry) from the same master data file by selectively including or rephrasing content. The entire build process can be run locally or within a Docker container for perfect reproducibility.

---

## 2. Core Concepts & Architecture

### The Facet System
This is the most important piece of custom logic in the project. It enables content tailoring.

* **Definition**: A "facet" is a named version of the CV, like `academia` or `industry`. The active facet is chosen in `app/config.toml` via the `facet_to_generate` key.
* **Implementation**: The logic resides in `app/scripts/generate_tex.py` within the `_process_data_for_facet` function.
* **Mechanism**:
    1.  The script loads the content from the `.toml` file (e.g., `mariecurie_cv.toml`).
    2.  It iterates through list-based sections (like `[[experience]]` or `[[education]]`).
    3.  For each item in a section (e.g., a single job), it looks for fields whose values are tables. A common pattern is a `details` field:
        ```toml
        details.academia = ["Description for academia."]
        details.industry = ["Description for industry."]
        ```
    4.  The script replaces the entire `details` table with the list corresponding to the active facet. For example, if `facet_to_generate = "academia"`, the `details` field becomes just `["Description for academia."]`.
    5.  This processed data is then passed to the Jinja2 template for rendering.

### Configuration-Driven Workflow
The entire build process is controlled by `app/config.toml`. This file is the single source of truth for all settings. Key configurable aspects include:
* `cv_settings`: Defines the active **facet** and paths to content/template files.
* `build_settings`: Toggles between local and **Docker-based** builds.
* `output_settings`: Controls the output format (`pdf` or `tex`), filename, temporary file cleanup, and output directory structure (`auto` or `dump`).

### Jinja2 Templating with Custom Delimiters
The project uses Jinja2 to inject the processed TOML data into LaTeX templates. To avoid conflicts with LaTeX syntax, it uses custom delimiters.
* Blocks: `((* ... *))` (e.g., `((* for item in items *))`)
* Variables: `((( ... )))` (e.g., `((( item.role )))`)
* Comments: `((# ... #))`

The templates are modular, with a main template (`cv_template.tex.j2`) that includes partials (e.g., `_header.tex.j2`, `_experience.tex.j2`) from the `app/templates/partials/` directory.

### Dockerized Build Environment
To ensure consistent builds and avoid local LaTeX dependency hell, the project includes a `Dockerfile`.
* The `Dockerfile` sets up a `python:3.10-slim` image and installs a full TeX Live distribution.
* When `use_docker = true` in `config.toml`, the `app/main.py` script will automatically:
    1.  Build a Docker image named `latex-cv`.
    2.  Re-run itself inside a new container, mounting the project directory.
    3.  Execute the PDF compilation using the `pdflatex` available in the container.
    4.  Prune the temporary image after the build.

---

## 3. Key Files & Directory Structure

```
.
├── app/                  # Main application source code
│   ├── content/          # Data Layer: CV content files (.toml)
│   │   └── mariecurie_cv.toml
│   ├── templates/        # Presentation Layer: Jinja2/LaTeX templates (.j2)
│   │   ├── cv_template.tex.j2 # Main template file
│   │   └── partials/        # Reusable template components
│   ├── assets/           # Static assets (e.g., signature PDFs, icons)
│   ├── scripts/          # Helper Python scripts for specific tasks
│   │   ├── generate_tex.py  # Core logic: processes data and renders templates
│   │   ├── assets.py        # Manages copying assets to the build folder
│   │   └── clean_tex.py     # Cleans up temporary LaTeX files (.aux, .log)
│   ├── config.toml       # Primary configuration file for the entire project
│   └── main.py           # Orchestrator: Main entry point that ties everything together
├── output/               # Default directory for all generated files (PDFs, .tex)
├── Dockerfile            # Defines the reproducible Docker build environment
├── pyproject.toml        # Project metadata, dependencies, and task runner definitions
└── README.md             # Project documentation for human users
```
---

## 4. Execution Workflow & Commands

The project uses `taskipy` as a task runner, configured in `pyproject.toml`. The primary commands are executed via `uv run`.

### Primary Command: `uv run build`
This is the main command to generate the CV. It executes `python app/main.py` and triggers the following sequence:

1.  **Entry Point**: `main_entry()` in `main.py` is called.
2.  **Config Load**: It loads `app/config.toml`.
3.  **Docker Check**: It checks the `use_docker` flag.
    * If `true` and not already inside Docker, it builds the Docker image and re-runs the script inside a container. The rest of the steps then happen inside Docker.
    * If `false` or already inside Docker, it proceeds directly.
4.  **Main Logic**: The `main()` function in `main.py` takes over.
5.  **Output Directory**: It creates the output directory based on the `output_mode` setting (`auto` for timestamped folder, `dump` for flat output).
6.  **TeX Generation**: It calls `generate()` from `app/scripts/generate_tex.py`. This function reads the content, processes it for the selected facet, and renders the Jinja2 template to create a `.tex` file in the output directory.
7.  **Format Check**:
    * If `output_format` is `tex`, the script finishes here.
    * If `output_format` is `pdf`, it continues.
8.  **Asset Copying**: It copies the contents of `app/assets/` into the output directory so LaTeX can find files like the signature PDF.
9.  **PDF Compilation**: It runs the `pdflatex` command on the generated `.tex` file.
10. **Cleanup**: If `cleanup_temp_files` is `true`, it deletes the intermediate LaTeX files (`.aux`, `.log`, etc.) and the copied assets folder from the output directory.

### Cleanup Command: `uv run purge`
This command is a simple utility to clean the `output/` directory. It runs `app/scripts/clear_output.py`, which deletes all files and subdirectories within `output/` but leaves the directory itself.

---

## 5. Data Schema (`.toml` content file)

The content `.toml` files (e.g., `mariecurie_cv.toml`) follow a consistent structure.

* **Top-Level Sections**: Each main part of the CV is a TOML table.
    * `[profile]`: A single table for personal contact information.
    * `[signature]`: A single table for signature details.
    * `[[education]]`, `[[experience]]`, `[[skills]]`, etc.: An array of tables, where each block represents a distinct entry (e.g., one job, one degree).
* **Item Structure**: Each item within an array of tables (like an `[[experience]]` block) contains key-value pairs.
    * `role = "..."`
    * `company = "..."`
    * `date = "..."`
* **Facet-Specific Content**: The facet system is implemented by making a field (commonly `details`) a table itself, with keys matching the facet names.
    ```toml
    # Example from [[education]]
    degree = "Doctor of Science"
    # ...
    details.academia = [ "Details for an academic audience." ]
    details.industry = [ "Details for an industry audience." ]
    ```
    During processing, the entire `details` table will be replaced by the list corresponding to the active facet.