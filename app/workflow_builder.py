import json
from pathlib import Path
from app.model import GenerateRequest

WORKFLOW_TEMPLATE_PATH = Path("workflow/flux_1_kontext_dev_FH.json")

def load_workflow_template():
    with open(WORKFLOW_TEMPLATE_PATH, "r", encoding="utf-8") as f:
        return json.load(f)

def build_workflow(req: GenerateRequest, prompt: str, input_image_name: str):
    workflow = load_workflow_template()

    filename_base = f"{req.trigger_word}_{req.expression}_{(req.index):05d}_"

    workflow["192"]["inputs"]["text"] = prompt
    workflow["136"]["inputs"]["filename_prefix"] = f"{req.trigger_word}_{req.expression}" 
    workflow["189"]["inputs"]["prefix"] = req.trigger_word
    workflow["190"]["inputs"]["file"] = f"{filename_base}.txt"
    workflow["142"]["inputs"]["image"] = f"{input_image_name} [output]"

    return workflow
