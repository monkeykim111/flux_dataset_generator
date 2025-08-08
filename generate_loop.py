import requests
import time
import itertools

API_URL = "http://localhost:8000/generateDataset"

# --- Configuration ---
# 'shot_type' or 'expression'
GENERATION_MODE = "expression" 

# For 'shot_type' mode
SHOT_TYPE_CHARACTERS = ["ellie", "ryder"]
NUM_SAMPLES_PER_SHOT_TYPE = 100

# For 'expression' mode
# EXPRESSION_CHARACTERS = ["ellie", "ryder"]
# EXPRESSIONS = ["smile", "angry", "sad"]
EXPRESSION_CHARACTERS = ["ryder"]
EXPRESSIONS = ["smile", "angry", "sad"]
ANGLES = ["front", "left_three_quarter", "right_three_quarter"]
NUM_SAMPLES_PER_EXPRESSION = 1
# --- End Configuration ---

def get_trigger_word(character_name):
    return f"fh_{character_name}"

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
