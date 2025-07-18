import glob
import os


def clean_auxiliary_tex_files(directory):
    """
    Remove LaTeX auxiliary files from the specified directory.

    Parameters:
    - directory (str): Path to the directory where LaTeX files are located. Defaults to current directory.
    """
    extensions = [
        "*.aux",
        "*.log",
        "*.out",
        "*.toc",
        "*.lof",
        "*.lot",
        "*.fls",
        "*.fdb_latexmk",
        "*.synctex.gz",
        "*.nav",
        "*.snm",
    ]

    deleted_files = []
    for ext in extensions:
        files = glob.glob(os.path.join(directory, ext))
        for file in files:
            try:
                os.remove(file)
                deleted_files.append(file)
            except OSError as e:
                print(f"❌  Failed to delete {file}: {e}")
