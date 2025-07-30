import requests
import time

API_URL = "http://localhost:8000/generateDataset"
# TRIGGER_WORD = "fh_ellie"
TRIGGER_WORD = "fh_ryder"
NUM_SAMPLES = 50

for i in range(NUM_SAMPLES):
    payload = {
        "trigger_word": TRIGGER_WORD,
        "index": i + 1
    }

    print(f"▶ Sending request {i+1}/{NUM_SAMPLES}")
    try:
        res = requests.post(API_URL, json=payload, timeout=300)

        if res.ok:
            print("✅ Success:", res.json()["prompt"])
        else:
            print("❌ Failed:", res.text)
    except requests.exceptions.RequestException as e:
        print(f"❌ Request failed: {e}")