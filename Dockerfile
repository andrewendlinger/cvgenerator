# Base image with Python and TeX Live
FROM python:3.10-slim

# Install basic utilities and TeX Live
RUN apt-get update && apt-get install -y \
    texlive-latex-recommended \
    texlive-latex-extra \
    texlive-fonts-recommended \
    texlive-font-utils \
    texlive-xetex \
    texlive-fonts-extra \
    latexmk \
    lmodern \
    git \
    make \
    ca-certificates \
    fonts-freefont-otf \
    fontconfig \
    && apt-get clean && rm -rf /var/lib/apt/lists/*

# Install Python dependencies
RUN pip install --no-cache-dir jinja2 toml

# Set the working directory
WORKDIR /app

# Copy the entire application source
COPY app/ .

# Entry point is now the main orchestrator script
CMD ["python", "main.py"]