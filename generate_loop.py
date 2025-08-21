import requests
import time
import itertools

API_URL = "http://localhost:8000/generateDataset"

# --- Configuration ---
# 'shot_type' or 'expression'
# GENERATION_MODE = "expression" 
GENERATION_MODE = "expression" 

# For 'shot_type' mode
SHOT_TYPE_CHARACTERS = ["lazie"]
NUM_SAMPLES_PER_SHOT_TYPE = 500

# For 'expression' mode
# EXPRESSION_CHARACTERS = ["ellie", "ryder"]
# EXPRESSIONS = ["smile", "angry", "sad"]
# EXPRESSION_CHARACTERS = ["ryder"]
# EXPRESSIONS = ["smile", "angry", "sad"]
EXPRESSION_CHARACTERS = ["lazie"]
EXPRESSIONS = ["smile", "angry", "sad"]
ANGLES = ["front", "left_three_quarter", "right_three_quarter"]
NUM_SAMPLES_PER_EXPRESSION = 170
# --- End Configuration ---

def get_trigger_word(character_name, prefix=None):
    """
    캐릭터명과 프리픽스를 조합하여 트리거 워드를 생성합니다.
    
    Args:
        character_name (str): 캐릭터 이름 (예: "ellie", "ryder", "lazie")
        prefix (str, optional): 사용할 프리픽스. None일 경우 캐릭터별 기본값 사용
    
    Returns:
        str: 트리거 워드 (예: "fh_ellie", "gb_lazie")
    
    기본 프리픽스:
    - ellie, ryder: "fh" (기존)
    - lazie: "gb" (신규)
    """
    if prefix is None:
        # 캐릭터별 기본 프리픽스 설정
        if character_name in ["ellie", "ryder"]:
            prefix = "fh"
        elif character_name == "lazie":
            prefix = "gb"
        else:
            # 알 수 없는 캐릭터의 경우 기본값으로 "fh" 사용
            prefix = "fh"
    
    return f"{prefix}_{character_name}"

def run_shot_type_generation():
    print("🚀 Starting generation in 'shot_type' mode.")
    # Use a global counter for unique indices
    global_index = 0
    for char in SHOT_TYPE_CHARACTERS:
        trigger_word = get_trigger_word(char)
        for i in range(NUM_SAMPLES_PER_SHOT_TYPE):
            global_index += 1
            payload = {
                "generation_mode": "shot_type",
                "trigger_word": trigger_word,
                "character_name": char,
                "index": global_index
            }
            send_request(payload, f"{global_index}/{len(SHOT_TYPE_CHARACTERS) * NUM_SAMPLES_PER_SHOT_TYPE}")

def run_expression_generation():
    print("🚀 Starting generation in 'expression' mode.")
    combinations = list(itertools.product(EXPRESSION_CHARACTERS, EXPRESSIONS, ANGLES))
    total_requests = len(combinations) * NUM_SAMPLES_PER_EXPRESSION
    
    # Use a single, global counter for the index across all combinations
    global_index = 0

    for char, expression, angle in combinations:
        trigger_word = get_trigger_word(char)
        print(f"\n--- Generating for {char} - {expression} - {angle} ---")
        for _ in range(NUM_SAMPLES_PER_EXPRESSION):
            global_index += 1
            payload = {
                "generation_mode": "expression",
                "trigger_word": trigger_word,
                "character_name": char,
                "expression": expression,
                "angle": angle,
                "index": global_index # Pass the unique, incrementing index
            }
            send_request(payload, f"{global_index}/{total_requests}")

def send_request(payload, progress):
    print(f"▶ [{progress}] Sending request: {payload}")
    try:
        res = requests.post(API_URL, json=payload, timeout=300)
        if res.ok:
            print(f"✅ Success: {res.json().get('prompt', 'N/A')}")
        else:
            print(f"❌ Failed: {res.text}")
    except requests.exceptions.RequestException as e:
        print(f"❌ Request failed: {e}")
    time.sleep(1)

if __name__ == "__main__":
    if GENERATION_MODE == "shot_type":
        run_shot_type_generation()
    elif GENERATION_MODE == "expression":
        run_expression_generation()
    else:
        print(f"❌ Invalid GENERATION_MODE: '{GENERATION_MODE}'. Please use 'shot_type' or 'expression'.")
