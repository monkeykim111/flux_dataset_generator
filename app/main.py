from fastapi import FastAPI, HTTPException
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
    logging.info(f"🚀 Request received for mode: {req.generation_mode}, index: {req.index}")
    shot_type = None

    if req.generation_mode == "shot_type":
        # --- Shot Type Mode Logic ---
        shot_type_map = {0: "closeup", 1: "bustShot", 2: "fullShot", 3: "kneeShot"}
        shot_type = shot_type_map[req.index % 4]
        
        input_image_name = f"{shot_type}_{req.trigger_word}.png"
        prompt_set_filename = f"{req.character_name}/{shot_type}/PromptSet.json"
        
    elif req.generation_mode == "expression":
        # --- Expression Mode Logic ---
        if not req.expression or not req.angle:
            raise HTTPException(status_code=400, detail="Expression and angle are required for expression mode.")
        
        input_image_name = f"bustShot_{req.trigger_word}_{req.expression}_{req.angle}.png"
        prompt_set_filename = f"{req.character_name}/{req.expression}/{req.angle}_PromptSet.json"

    else:
        raise HTTPException(status_code=400, detail=f"Invalid generation mode: {req.generation_mode}")

    logging.info(f"ℹ️ Using prompt set: {prompt_set_filename}")
    logging.info(f"🖼️ Using input image: {input_image_name}")
    
    try:
        prompt_set = load_prompt_set(prompt_set_filename)
    except FileNotFoundError:
        logging.error(f"❌ Prompt set file not found: {prompt_set_filename}")
        raise HTTPException(status_code=404, detail=f"Prompt set file not found: {prompt_set_filename}")

    prompt = generate_prompt(prompt_set)
    
    workflow = build_workflow(req, prompt, input_image_name)
    client_id = str(uuid.uuid4())
    node_ids = set(workflow.keys())

    payload = {"prompt": workflow, "client_id": client_id}

    async with httpx.AsyncClient() as client:
        res = await client.post(COMFYUI_API_URL, json=payload, timeout=20)
        res.raise_for_status()
        prompt_id = res.json()["prompt_id"]
        logging.info(f"✅ Job sent to ComfyUI. Prompt ID: {prompt_id}. Tracking {len(node_ids)} nodes.")

    # WebSocket connection to track progress
    ws_url = f"{COMFYUI_WS_URL}?clientId={client_id}"
    async with websockets.connect(ws_url) as websocket:
        logging.info(f"⏳ Waiting for job completion (Prompt ID: {prompt_id})...")
        while True:
            out = await websocket.recv()
            if isinstance(out, str):
                message = json.loads(out)
                if message.get('type') == 'executed' and message.get('data', {}).get('prompt_id') == prompt_id:
                    logging.info(f"🎉 Job completed (Prompt ID: {prompt_id}).")
                    break

    logging.info(f"✅ Request for index {req.index} finished.")
    
    # Use index + 1 to start numbering from 1.
    output_image_name = f"{req.trigger_word}_{(req.index):05d}_.png"

    return {
        "status": "ok",
        "prompt": prompt,
        "image": output_image_name
    }
