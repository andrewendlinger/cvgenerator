# app/scripts/generate_tex.py

from pathlib import Path

import toml
from jinja2 import Environment, FileSystemLoader

# --- TOML Structure Keys & Defaults ---
SETTINGS_TABLE = "cv_settings"
TAGS_KEY = "tags"
DETAILS_FALLBACK_facet = "academia"
UNIVERSAL_TAG = "all"

# --- Jinja2 Configuration ---
JINJA_CONFIG = {
    "block_start_string": "((*",
    "block_end_string": "*))",
    "variable_start_string": "(((",
    "variable_end_string": ")))",
    "comment_start_string": "((#",
    "comment_end_string": "#))",
    "trim_blocks": True,
    "lstrip_blocks": True,
}


def _process_data_for_facet(data, facet):
    """
    Dynamically processes CV data for a specific facet.

    This function performs two main tasks:
    1.  It filters out entire items from lists (like a job in 'experience')
        if their 'tags' do not match the selected facet.
    2.  It scans every field within an item. If a field's value is a
        dictionary containing facet keys (e.g., 'academic', 'industry'),
        it replaces that dictionary with the value matching the current facet.
    """
    processed_data = data.copy()
    for section_name, section_content in processed_data.items():
        if not isinstance(section_content, list):
            continue  # Skip sections that aren't lists of items

        filtered_and_processed_items = []
        for item in section_content:
            if not isinstance(item, dict):
                # very unusual, but just in case something doesn't have a key
                filtered_and_processed_items.append(item)
                continue

            # 1. Filter the entire item based on its tags
            tags = item.get(TAGS_KEY, [UNIVERSAL_TAG])
            if UNIVERSAL_TAG not in tags and facet not in tags:
                continue  # Skip this item if its tags don't match the facet

            processed_item = item.copy()

            # Generalised processing for any field in the item
            for key, value in item.items():
                if not isinstance(value, dict):
                    continue  # Field is not a dictionary, no need to process

                # Check if the dictionary contains facet-specific content.
                # Try the target facet first, then the fallback.
                resolved_value = value.get(facet, value.get(DETAILS_FALLBACK_facet))

                # If a facet-specific value was found, update the item.
                # Otherwise, leave the original dictionary untouched (e.g., a date object).
                if resolved_value is not None:
                    processed_item[key] = resolved_value

            filtered_and_processed_items.append(processed_item)

        processed_data[section_name] = filtered_and_processed_items
    return processed_data


def generate(config_path: Path, output_tex_path: Path):
    """
    Generates a single .tex file based on a config file.

    Args:
        config_path: Absolute path to the config.toml file.
        output_tex_path: Absolute path where the final .tex file will be saved.
    """
    config_dir = config_path.parent

    # 1. Load Configuration
    config = toml.load(config_path)
    settings = config.get(SETTINGS_TABLE, {})
    facet = settings.get("facet_to_generate", "academic")

    # 2. Resolve Paths & Load Data
    content_file = (config_dir / settings["content_file_name"]).resolve()
    template_full_path = (config_dir / settings["template_file_name"]).resolve()
    cv_data = toml.load(content_file)

    # 3. Process Data
    print(f"➡️  Processing facet: {facet}")
    processed_data = _process_data_for_facet(cv_data, facet)

    # 4. Render Template
    template_dir = template_full_path.parent
    template_name = template_full_path.name
    env = Environment(loader=FileSystemLoader(template_dir), **JINJA_CONFIG)
    template = env.get_template(template_name)
    render_context = {**processed_data, **settings}
    rendered_tex = template.render(render_context)

    # 5. Write Output .tex File
    with open(output_tex_path, "w", encoding="utf-8") as f:
        f.write(rendered_tex)
    print(f"➡️  LaTeX source generated:  {output_tex_path.name}")
