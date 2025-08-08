import json
from pathlib import Path
from app.model import GenerateRequest

# 워크플로우 템플릿 파일 경로
WORKFLOW_TEMPLATE_PATH = Path("workflow/flux_1_kontext_dev_FH.json")

def load_workflow_template():
    """워크플로우 템플릿 JSON 파일을 불러옵니다."""
    with open(WORKFLOW_TEMPLATE_PATH, "r", encoding="utf-8") as f:
        return json.load(f)

def build_workflow(req: GenerateRequest, prompt: str, input_image_name: str):
    """
    요청 정보를 바탕으로 ComfyUI 워크플로우를 구성합니다.

    Args:
        req (GenerateRequest): API 요청 모델 객체
        prompt (str): 생성된 전체 프롬프트 문자열
        input_image_name (str): 사용할 입력 이미지 파일명

    Returns:
        dict: ComfyUI에 전송할 워크플로우 딕셔너리
    """
    workflow = load_workflow_template()

    if req.generation_mode == "expression":
        # 'expression' 모드에서는 expression을 파일명에 포함
        text_filename_base = f"{req.trigger_word}_expression_{(req.index):05d}_"
        image_filename_prefix = f"{req.trigger_word}_expression"
    else:
        # 'shot_type' 모드에서는 expression을 파일명에 포함하지 않음
        text_filename_base = f"{req.trigger_word}_{(req.index):05d}_"
        image_filename_prefix = f"{req.trigger_word}"
    
    # 워크플로우의 각 노드에 필요한 값을 채워넣음
    workflow["192"]["inputs"]["text"] = prompt
    workflow["136"]["inputs"]["filename_prefix"] = image_filename_prefix
    workflow["189"]["inputs"]["prefix"] = req.trigger_word
    workflow["190"]["inputs"]["file"] = f"{text_filename_base}.txt"
    workflow["142"]["inputs"]["image"] = f"{input_image_name} [output]"

    return workflow
