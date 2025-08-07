from fastapi import FastAPI, HTTPException
from app.model import GenerateRequest
from app.prompt_util import generate_prompt, load_prompt_set
from app.workflow_builder import build_workflow
import httpx
import websockets
import json
import uuid
import logging
import random
import glob
from pathlib import Path

# --- 기본 설정 ---
# 로깅 설정: 시간, 로그 레벨, 메시지 형식 지정
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

# ComfyUI API 및 웹소켓 주소
COMFYUI_API_URL = "http://localhost:9000/prompt"
COMFYUI_WS_URL = "ws://localhost:9000/ws"
# ComfyUI의 입력 이미지가 저장된 디렉토리 (사용자 지정 경로)
COMFYUI_INPUT_DIR = Path("/home/jonathan/Desktop/NewSSD500GB/newssd/pythonProject/ComfyUI/output")

# FastAPI 앱 생성
app = FastAPI()

# --- API 엔드포인트 ---
@app.post("/generateDataset")
async def generate_dataset(req: GenerateRequest):
    """데이터셋 생성을 위한 메인 API 엔드포인트"""
    logging.info(f"🚀 생성 모드({req.generation_mode}), 인덱스({req.index}) 요청 접수")
    shot_type = None

    # 1. 생성 모드에 따라 프롬프트와 입력 이미지 결정
    if req.generation_mode == "shot_type":
        # --- '샷 타입' 모드 ---
        shot_type_map = {0: "closeup", 1: "bustShot", 2: "fullShot", 3: "kneeShot"}
        shot_type = shot_type_map[req.index % 4]
        
        input_image_name = f"{shot_type}_{req.trigger_word}.png"
        prompt_set_filename = f"{req.character_name}/{shot_type}/PromptSet.json"
        
    elif req.generation_mode == "expression":
        # --- '표정' 모드 ---
        if not req.expression or not req.angle:
            raise HTTPException(status_code=400, detail="'표정' 모드에서는 expression과 angle 값이 반드시 필요합니다.")
        
        # 표정과 앵글에 맞는 입력 이미지들을 동적으로 찾아 랜덤 선택
        image_pattern = f"bustShot_{req.trigger_word}_{req.expression}_{req.angle}_*.png"
        image_files = glob.glob(str(COMFYUI_INPUT_DIR / image_pattern))
        
        if not image_files:
            # 해당 패턴의 입력 이미지를 찾지 못하면 즉시 에러 발생
            error_msg = f"입력 이미지를 찾을 수 없습니다. 경로: '{COMFYUI_INPUT_DIR}', 패턴: '{image_pattern}'"
            logging.error(error_msg)
            raise HTTPException(status_code=404, detail=error_msg)
            
        # 찾은 이미지 중 하나를 랜덤으로 선택
        selected_image_path = Path(random.choice(image_files))
        input_image_name = selected_image_path.name
        logging.info(f"'{image_pattern}' 패턴으로 {len(image_files)}개의 이미지 발견. 랜덤 선택: {input_image_name}")

        prompt_set_filename = f"{req.character_name}/{req.expression}/{req.angle}_PromptSet.json"

    else:
        raise HTTPException(status_code=400, detail=f"잘못된 생성 모드입니다: {req.generation_mode}")

    logging.info(f"ℹ️ 프롬프트셋 파일: {prompt_set_filename}")
    logging.info(f"🖼️ 입력 이미지 파일: {input_image_name}")
    
    # 2. 프롬프트 생성 및 워크플로우 빌드
    try:
        prompt_set = load_prompt_set(prompt_set_filename)
    except FileNotFoundError:
        logging.error(f"❌ 프롬프트셋 파일을 찾을 수 없습니다: {prompt_set_filename}")
        raise HTTPException(status_code=404, detail=f"프롬프트셋 파일을 찾을 수 없습니다: {prompt_set_filename}")

    prompt = generate_prompt(prompt_set)
    workflow = build_workflow(req, prompt, input_image_name)
    
    # 3. ComfyUI에 생성 요청 전송
    client_id = str(uuid.uuid4())
    payload = {"prompt": workflow, "client_id": client_id}

    async with httpx.AsyncClient() as client:
        res = await client.post(COMFYUI_API_URL, json=payload, timeout=20)
        res.raise_for_status()
        prompt_id = res.json()["prompt_id"]
        logging.info(f"✅ ComfyUI에 작업 전송 완료. 프롬프트 ID: {prompt_id}")

    # 4. 웹소켓으로 작업 완료 '확실하게' 대기 (try/except 제거)
    # 이제 웹소켓 연결 실패 시, 에러가 발생하여 generate_loop.py가 다음 요청을 보내지 않습니다.
    ws_url = f"{COMFYUI_WS_URL}?clientId={client_id}"
    async with websockets.connect(ws_url) as websocket:
        logging.info(f"⏳ 작업 완료 대기 중 (프롬프트 ID: {prompt_id})...")
        while True:
            out = await websocket.recv()
            if isinstance(out, str):
                message = json.loads(out)
                if message.get('type') == 'executed' and message.get('data', {}).get('prompt_id') == prompt_id:
                    logging.info(f"🎉 작업 완료 (프롬프트 ID: {prompt_id}).")
                    break
        
    logging.info(f"✅ 인덱스({req.index}) 요청 처리 완료.")
    
    # 5. API 응답 반환
    output_image_name = f"{req.trigger_word}_{(req.index):05d}_.png"

    return {
        "status": "ok",
        "prompt": prompt,
        "image": output_image_name
    }
