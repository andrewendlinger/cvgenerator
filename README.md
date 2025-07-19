<h1>
  <img src="./app/assets/icon_cvgen.svg" alt="icon" width="100">&nbsp;&nbsp;CV Generator
</h1>

[![uv](https://img.shields.io/endpoint?url=https://raw.githubusercontent.com/astral-sh/uv/main/assets/badge/v0.json)](https://github.com/astral-sh/uv)
[![Ruff](https://img.shields.io/endpoint?url=https://raw.githubusercontent.com/astral-sh/ruff/main/assets/badge/v2.json)](https://github.com/astral-sh/ruff)
![Tests](https://github.com/andrewendlinger/cvgenerator/actions/workflows/test_build_process.yml/badge.svg)


A tool to generate **formatted, tailored PDF CVs** from a simple text file.

<p>&nbsp;</p>
<p align="center" style="font-size:18px;">
  📦 <a href="./app/content/mariecurie_cv.toml"><b>TOML input</b></a> &nbsp;&rarr;&nbsp;
  ⚙️ <em>Python + LaTeX </em> &nbsp;&rarr;&nbsp;
  📄 <a href="./output/demo/CV_MarieCurie_2025.pdf"><b>PDF output</b></a>
</p>
<p>&nbsp;</p>



## ✨ About The Project

I got tired of juggling multiple CV versions — academic, industry, grants — and constantly editing `.tex` files. So, I built this tool to separate **content** (your info) from **design** (the LaTeX template) and make CV updates easy.



* Using a single TOML ([toml?](https://toml.io/en/)) file plus *facets*, you can quickly create different CV versions with one command.
* Docker support means no LaTeX install is needed.

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
# with uv (recommended) 
uv sync

# or:
# pip install .
```

---

## Usage

Build Your CV

```bash
# (recommended)
uv run task build

# or:
# python app/main.py
```

Clean the Output Directory

To remove generated files:

```bash
# (recommended)
uv run task purge

# or: 
# python app/scripts/clear_output.py
```

---

## ⚙️ How It Works

This system revolves around **three main components**:

### 1. Content File

Located in [`app/content/`](./app/content/mariecurie_cv.toml) is a TOML file that stores your **personal details, experience, education, and skills**.

Each entry can include **facets** to generate different versions of the CV — for example, targeting academia vs. industry:

```toml

[[education]]
degree = "Doctor of Science in Physics"
institution = "University of Paris (Sorbonne)"
# first facet
details.academia = [ 
    "Thesis established the new scientific field of radioactivity..."
]
# second facet
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

----

## 🐳 Docker Workflow

Use Docker for consistent builds across systems and to **avoid any local LaTeX setup or dependency issues**.

To use docker, simply:

1. In [`config.toml`](./app/config.toml), set:  `use_docker = true`
2. Start the build (`uv run task build`)

> Under the hood this will:
> * Automatically build the Docker image
> * Mount your project into the container
> * Compile your CV to PDF or LaTeX


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
