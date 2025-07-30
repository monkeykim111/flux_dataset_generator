import json
from pathlib import Path
import random

PROMPT_SET_PATH = Path("data/PromptSet.json")

def load_prompt_set(filename: str = "PromptSet.json"):
    prompt_set_path = Path("data") / filename
    with open(prompt_set_path, 'r', encoding='utf-8') as f:
        return json.load(f)

def generate_prompt(prompt_set):
    lines = []
    for category in prompt_set:
        sentence = random.choice(category["prompts"])
        if not sentence.endswith("."):
            sentence += "."
        lines.append(sentence)
    return " ".join(lines)


