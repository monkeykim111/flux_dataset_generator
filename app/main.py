from fastapi import FastAPI
from app.model import GenerateRequest
from app.prompt_util import generate_prompt, load_prompt_set
from app.workflow_builder import build_workflow
import httpx
import websockets
import json
import uuid
import logging

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

COMFYUI_API_URL = "http://localhost:9000/prompt"
COMFYUI_WS_URL = "ws://localhost:9000/ws"
app = FastAPI()


@app.post("/generateDataset")
async def generate_dataset(req: GenerateRequest):
    logging.info(f"🚀 Request received for index: {req.index}")

    # shot_type_map = {
    #     0: "closeup",
    #     1: "bustShot",
    #     2: "fullShot",
    #     3: "kneeShot"
    # }
    # shot_type = shot_type_map[req.index % 4]
    shot_type = "fullShot"

    input_image_name = f"{shot_type}_{req.trigger_word}.png"
    prompt_set_filename = f"{shot_type}_PromptSet_ryder.json"
    # prompt_set_filename = f"{shot_type}_PromptSet.json"
    logging.info(f"ℹ️ Using prompt set: {prompt_set_filename}")
    
    try:
        prompt_set = load_prompt_set(prompt_set_filename)
    except FileNotFoundError:
        logging.warning(f"'{prompt_set_filename}' not found. Falling back to default 'PromptSet.json'.")
        prompt_set = load_prompt_set()

    prompt = generate_prompt(prompt_set)
    workflow = build_workflow(req.trigger_word, req.index, prompt, input_image_name)
    client_id = str(uuid.uuid4())
    node_ids = set(workflow.keys())

    payload = {
        "prompt": workflow,
        "client_id": client_id
    }

    async with httpx.AsyncClient() as client:
        res = await client.post(COMFYUI_API_URL, json=payload)
        res.raise_for_status()
        prompt_id = res.json()["prompt_id"]
        logging.info(f"✅ Job sent to ComfyUI. Prompt ID: {prompt_id}. Tracking {len(node_ids)} nodes.")

    # 1. 웹소켓 연결 주소 생성
    ws_url = f"{COMFYUI_WS_URL}?clientId={client_id}"

    # 2. 웹소켓 연결 및 메시지 수신 루프 시작
    async with websockets.connect(ws_url) as websocket:
        logging.info(f"⏳ Waiting for job completion (Prompt ID: {prompt_id})...")
        finished_nodes = set()
        while True:
            # 3. Comfyui로 부터 메시지가 올 때까지 대기
            out = await websocket.recv()
            if isinstance(out, str):
                # 받은 json 문자열을 파이썬 객체로 변환
                message = json.loads(out)

                # 4. 'progress_state' 메시지 처리 (모든 노드 완료 체크 방식)
                if message.get('type') == 'progress_state' and message.get('data', {}).get('prompt_id') == prompt_id:
                    nodes_data = message.get('data', {}).get('nodes', {})
                    for node_id, node_info in nodes_data.items():
                        if node_info.get('state') == 'finished':
                            finished_nodes.add(node_id)
                    
                    if node_ids.issubset(finished_nodes):
                        logging.info(f"🎉 Job completed (Prompt ID: {prompt_id}).")
                        break
                # 5. 'executed' 메시지 처리 (최종 완료 신호 방식)    
                elif message.get('type') == 'executed' and message.get('data', {}).get('prompt_id') == prompt_id:
                    logging.info(f"🎉 Job completed (Prompt ID: {prompt_id}).")
                    break

    logging.info(f"✅ Request for index {req.index} finished.")
    return {
        "status": "ok",
        "prompt": prompt,
        "image": f"{req.trigger_word}_{req.index:05d}.png"
    }
