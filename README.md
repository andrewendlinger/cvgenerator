<h1>
  <img src="./app/assets/icon_cvgen.svg" alt="icon" width="100" style="vertical-align: middle; margin-right: 15px;">
  CV Generator
</h1>

[![uv](https://img.shields.io/endpoint?url=https://raw.githubusercontent.com/astral-sh/uv/main/assets/badge/v0.json)](https://github.com/astral-sh/uv)
[![Ruff](https://img.shields.io/endpoint?url=https://raw.githubusercontent.com/astral-sh/ruff/main/assets/badge/v2.json)](https://github.com/astral-sh/ruff)

A tool to generate formatted, tailored PDF CVs from a simple text file. Stop manually editing `.tex` files for every job application and let this project automate the process for you. [Here is a demo](./output/demo/CV_MarieCurie_2025.pdf).

---

## ✨ About The Project

Managing multiple CV versions can be tedious — academic, industry, grant-specific, and more. This project separates **content** (your professional history) from **presentation** (the LaTeX template) to streamline this process.

With a single [TOML](https://toml.io/en/) file and a system of *facets*, you can define multiple CV versions and build them with one command. It supports Docker for full reproducibility without installing LaTeX locally.

#### Key Features

* **Single Source of Truth**
All CV data lives in one easy-to-edit TOML file.
* **Facet System**
Generate different CV versions (e.g., "academia", "industry") from the same data.
* **Customizable Templates**
Full control over layout using Jinja2 + LaTeX.
* **Dockerized Builds**
Build CVs in a clean containerized environment.
* **Flexible Configuration**
Control formats, filenames, cleanup, and output structure via `config.toml`.

---

## Getting Started

#### Prerequisites

* Python (3.10+)
* [uv](https://github.com/astral-sh/uv) (optional but recommended)
* [Docker Desktop](https://www.docker.com/get-started/) (optional but recommended)

#### Installation

Clone the repository:

```bash
git clone https://github.com/your-username/cv-generator.git
cd cv-generator
```

Install dependencies:

```bash
# with uv
uv sync
# or using pip
pip install .
```

---

## Usage

#### Build Your CV

**Recommended:** Use the `build` task:

```bash
uv run build
```

Or run the script directly:

```bash
python app/main.py
```

### 🧹 Clean the Output Directory

To remove generated files:

```bash
uv run purge
```

Equivalent to running:

```bash
python app/scripts/clear_output.py
```

---

## ⚙️ How It Works

This system revolves around **three main components**:

### 1. Content File

Located in [`app/content/`](./app/content/mariecurie_cv.toml), this TOML file defines your **personal details, experience, education, and skills**.

Each entry can include **facets** to generate different versions of the CV — for example, targeting academia vs. industry:

```toml
[[education]]
degree = "Doctor of Science in Physics"
institution = "University of Paris (Sorbonne)"
details.academia = [
    "Thesis established the new scientific field of radioactivity..."
]
details.industry = [
    "Discovered and characterized new materials (Polonium, Radium)..."
]
```
👉 See the full example: [`mariecurie_cv.toml`](./app/content/mariecurie_cv.toml)

The active facet is selected in the config file.


### 2. Configuration

The [config.toml](./app/config.toml) file is the control center for the build process.

Key sections:

| Section             | Key                  | Description                                         |
| ------------------- | -------------------- | --------------------------------------------------- |
| `[cv_settings]`     | `facet_to_generate`  | Select which version of the CV to generate          |
|                     | `content_file_name`  | Path to the TOML content file                       |
|                     | `template_file_name` | Path to the Jinja2-LaTeX template                   |
| `[build_settings]`  | `use_docker`         | Build with Docker or local LaTeX                    |
| `[output_settings]` | `output_format`      | `pdf` (default) or `tex` (for LaTeX source only)    |
|                     | `cleanup_temp_files` | Remove intermediate files like `.aux`, `.log`, etc. |
|                     | `output_mode`        | `auto` (timestamped folder) or `dump` (flat output) |
|                     | `base_filename`      | Custom output filename (e.g. `CV_MarieCurie_2025`)  |

---

Here’s an improved and more polished version of that section — it's clearer, slightly more formal, and structured for easy readability:

### 3. Templates

Template files are located in [`/app/templates/`](./app/templates/) and define the overall layout of the CV using **LaTeX + Jinja2**. These templates are populated with the content defined in your TOML file.

* [`cv_template.tex.j2`](./app/templates/cv_template.tex.j2): The main document structure.
* [`partials/`](./app/templates/partials/): Modular components for specific sections such as:

  * `_header.tex.j2`
  * `_skills.tex.j2`
  * `_experience.tex.j2`
  * `_education.tex.j2`
  * ...

Together, these templates control the **visual style**, **structure**, and **content placement** in the final document.

---

## 🐳 Docker Workflow

Use Docker for consistent builds across systems and to **avoid any local LaTeX setup or dependency issues**.

### Steps:

1. In [`config.toml`](./app/config.toml), set:

   ```toml
   use_docker = true
   ```

2. Build the CV:

   ```bash
   uv run build
   ```

This will:

* Automatically build the Docker image
* Mount your project into the container
* Compile your CV to PDF or LaTeX


## 📂 Project Structure

```
.
├── app/
│   ├── content/         # Your CV data files (.toml)
│   ├── templates/       # Jinja2 LaTeX templates (.j2)
│   ├── assets/          # Static assets like a signature image
│   ├── scripts/         # Helper Python scripts
│   ├── config.toml      # Main configuration file
│   └── main.py          # The orchestrator script
├── output/              # Generated CVs appear here
├── Dockerfile           # Defines the Docker build environment
├── pyproject.toml       # Project definition and dependencies
└── README.md            # You are here!
```

---

## 📄 License

Distributed under the MIT License.
