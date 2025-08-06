import json
from pathlib import Path

WORKFLOW_TEMPLATE_PATH = Path("workflow/flux_1_kontext_dev_FH.json")

def load_workflow_template():
    with open(WORKFLOW_TEMPLATE_PATH, "r", encoding="utf-8") as f:
        return json.load(f)
    

def build_workflow(trigger_word: str, index: int, prompt: str, input_image_name: str):
    text_filename = f"{trigger_word}_{index:05d}_.txt"
    workflow = load_workflow_template()
    workflow["192"]["inputs"]["text"] = prompt
    workflow["136"]["inputs"]["filename_prefix"] = trigger_word
    workflow["189"]["inputs"]["prefix"] = trigger_word
    workflow["190"]["inputs"]["file"] = text_filename
    workflow["142"]["inputs"]["image"] = f"{input_image_name} [output]"

    return workflow


