
import json
import re
from pathlib import Path


# -------------------------------
# Configuration
# -------------------------------

SOURCE_MD = Path("sklearn_topics.md")

OUTPUT_MD = Path("sklearn_topics_linked.md")

INDEX_NOTEBOOK = Path("sklearn_topics_index.ipynb")

NOTEBOOK_DIR = Path("notebooks")


# -------------------------------
# Helper functions
# -------------------------------

def create_slug(number, title):
    """Create a filesystem-friendly filename."""

    text = f"{number}_{title}"

    text = re.sub(r'[^\w.-]+', '_', text)

    return text.strip("_")


def create_notebook(title, number, output_path):
    """Create an empty Jupyter notebook for a topic."""

    output_path.parent.mkdir(parents=True, exist_ok=True)

    notebook = {
        "cells": [
            {
                "cell_type": "markdown",
                "metadata": {},
                "source": [
                    f"# {number}. {title}\n",
                    "\n",
                    "## Notes\n",
                    "\n",
                    "Add your learning notes here."
                ]
            },
            {
                "cell_type": "code",
                "execution_count": None,
                "metadata": {},
                "outputs": [],
                "source": []
            }
        ],
        "metadata": {
            "kernelspec": {
                "display_name": "Python 3",
                "language": "python",
                "name": "python3"
            },
            "language_info": {
                "name": "python"
            }
        },
        "nbformat": 4,
        "nbformat_minor": 5
    }

    with open(output_path, "w", encoding="utf-8") as file:
        json.dump(notebook, file, indent=2)

    print(f"Created: {output_path}")


def make_link(number, title, path):
    """Create a Markdown link."""

    relative_path = path.as_posix()

    return f"[{number}. {title}]({relative_path})"


# -------------------------------
# Main processing
# -------------------------------

if not SOURCE_MD.exists():
    raise FileNotFoundError(
        f"Markdown file not found: {SOURCE_MD}"
    )

NOTEBOOK_DIR.mkdir(exist_ok=True)

markdown = SOURCE_MD.read_text(encoding="utf-8")

lines = markdown.splitlines()

updated_lines = []

current_section = None
current_topic = None

notebook_count = 0


# Match numbered headings:
# ## 1. Supervised Learning
# ### 1.1. Linear Models

heading_pattern = re.compile(
    r'^(#{2,3})\s+(\d+(?:\.\d+)*\.?)\s+(.+?)\s*$'
)

# Match numbered list items:
# - 1.1.1. Ordinary Least Squares

item_pattern = re.compile(
    r'^(\s*[-*]\s+)(\d+(?:\.\d+)*\.?)\s+(.+?)\s*$'
)


for line in lines:

    heading_match = heading_pattern.match(line)

    item_match = item_pattern.match(line)

    # ---------------------------
    # Level 1: Main sections
    # ---------------------------

    if heading_match:

        level = len(heading_match.group(1))

        number = heading_match.group(2).rstrip(".")

        title = heading_match.group(3)

        if level == 2:

            current_section = (
                NOTEBOOK_DIR /
                create_slug(number, title)
            )

            current_topic = None

            notebook_path = (
                current_section /
                f"{create_slug(number, title)}.ipynb"
            )

        # -----------------------
        # Level 2: Subsections
        # -----------------------

        elif level == 3:

            if current_section is None:
                updated_lines.append(line)
                continue

            current_topic = (
                current_section /
                create_slug(number, title)
            )

            notebook_path = (
                current_section /
                f"{create_slug(number, title)}.ipynb"
            )

        else:
            updated_lines.append(line)
            continue

        create_notebook(
            title,
            number,
            notebook_path
        )

        notebook_count += 1

        link = make_link(
            number,
            title,
            notebook_path
        )

        updated_lines.append(
            f"{'#' * level} {link}"
        )

    # ---------------------------
    # Level 3: Individual topics
    # ---------------------------

    elif item_match:

        prefix = item_match.group(1)

        number = item_match.group(2).rstrip(".")

        title = item_match.group(3)

        if current_section is None or current_topic is None:
            updated_lines.append(line)
            continue

        notebook_path = (
            current_topic /
            f"{create_slug(number, title)}.ipynb"
        )

        create_notebook(
            title,
            number,
            notebook_path
        )

        notebook_count += 1

        link = make_link(
            number,
            title,
            notebook_path
        )

        updated_lines.append(
            f"{prefix}{link}"
        )

    else:

        updated_lines.append(line)


# -------------------------------
# Save updated Markdown
# -------------------------------

updated_markdown = "\n".join(updated_lines) + "\n"

OUTPUT_MD.write_text(
    updated_markdown,
    encoding="utf-8"
)


# -------------------------------
# Create master index notebook
# -------------------------------

index_notebook = {
    "cells": [
        {
            "cell_type": "markdown",
            "metadata": {},
            "source": updated_markdown.splitlines(keepends=True)
        }
    ],
    "metadata": {
        "kernelspec": {
            "display_name": "Python 3",
            "language": "python",
            "name": "python3"
        },
        "language_info": {
            "name": "python"
        }
    },
    "nbformat": 4,
    "nbformat_minor": 5
}

with open(INDEX_NOTEBOOK, "w", encoding="utf-8") as file:
    json.dump(index_notebook, file, indent=2)


# -------------------------------
# Summary
# -------------------------------

print("\n========== COMPLETED ==========")

print(f"Total notebooks created: {notebook_count}")

print(f"Notebook directory: {NOTEBOOK_DIR}")

print(f"Updated Markdown: {OUTPUT_MD}")

print(f"Master index: {INDEX_NOTEBOOK}")
