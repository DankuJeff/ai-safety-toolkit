import os
from pathlib import Path
from typing import Literal

import yaml
from pydantic import BaseModel, Field

LIBRARY_DIR = Path(__file__).parent / "library"

ExpectedBehavior = Literal["allow", "warn", "refuse"]


class Prompt(BaseModel):
    id: str
    category: str
    severity: int = Field(..., ge=1, le=5)
    expected_behavior: ExpectedBehavior
    prompt: str
    notes: str = ""


def load_library(categories: list[str] | None = None) -> list[Prompt]:
    """Load all prompts from YAML files. Optionally filter by category name(s)."""
    prompts: list[Prompt] = []

    for yaml_file in sorted(LIBRARY_DIR.glob("*.yaml")):
        cat_name = yaml_file.stem
        if categories and cat_name not in categories:
            continue

        with open(yaml_file, encoding="utf-8") as f:
            data = yaml.safe_load(f)

        for p in data["prompts"]:
            prompts.append(Prompt(category=cat_name, **p))

    return prompts


def load_by_id(prompt_id: str) -> Prompt | None:
    for p in load_library():
        if p.id == prompt_id:
            return p
    return None
