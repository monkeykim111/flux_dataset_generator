import json
import os
from pathlib import Path

# --- Configuration ---
CHARACTERS = ["ellie", "ryder"]
BASE_PATH = Path("data")

# Expression prompts (Korean: 웃음, 화남, 슬픔)
EXPRESSIONS = {
    "smile": ["a gentle smile with soft, happy eyes", "a bright, joyful smile showing teeth", "a subtle, warm smile"],
    "angry": ["a furious expression with narrowed eyes and a clenched jaw", "a stern, angry look with furrowed brows", "a look of intense anger with a downward-turned mouth"],
    "sad": ["a melancholic expression with downturned lips and sad eyes", "a sorrowful look with tears welling up in the eyes", "a look of deep sadness and despair"]
}

# Camera angle prompts (Korean: 정면, 왼쪽/오른쪽 정측면/완전측면/후측면)
ANGLES = {
    "front": ["a straight-on bust shot, centered, looking directly at the camera"],
    "left_three_quarter": ["a bust shot from a left three-quarter angle", "a bust shot from a complete left profile view", "a bust shot from a left rear three-quarter angle"],
    "right_three_quarter": ["a bust shot from a right three-quarter angle", "a bust shot from a complete right profile view", "a bust shot from a right rear three-quarter angle"]
}
# --- End Configuration ---

def create_expression_prompts():
    """
    Creates expression-based prompt sets for each character.
    It uses the existing bustShot prompt as a template and replaces
    the 'expression' and 'camera_angle' categories.
    """
    print("🚀 Starting creation of expression prompt sets...")

    for char in CHARACTERS:
        print(f"Processing character: {char}")

        # 1. Load base prompt set from bustShot
        base_prompt_file = BASE_PATH / char / "bustShot" / "PromptSet.json"
        try:
            with open(base_prompt_file, 'r', encoding='utf-8') as f:
                base_prompts = json.load(f)
            print(f"  ✅ Loaded base prompt from {base_prompt_file}")
        except FileNotFoundError:
            print(f"  ❌ ERROR: Base prompt file not found at {base_prompt_file}. Skipping {char}.")
            continue

        # 2. Generate new prompt files for each expression and angle
        for exp_name, exp_prompts in EXPRESSIONS.items():
            # Create expression directory
            expression_dir = BASE_PATH / char / exp_name
            expression_dir.mkdir(parents=True, exist_ok=True)

            for angle_name, angle_prompts in ANGLES.items():
                new_prompt_set = []
                # Replace categories
                for category in base_prompts:
                    if category["category"] == "expression":
                        new_prompt_set.append({"category": "expression", "prompts": exp_prompts})
                    elif category["category"] == "camera_angle":
                        new_prompt_set.append({"category": "camera_angle", "prompts": angle_prompts})
                    else:
                        new_prompt_set.append(category)

                # Write the new prompt file
                new_filename = f"{angle_name}_PromptSet.json"
                output_path = expression_dir / new_filename
                with open(output_path, 'w', encoding='utf-8') as f:
                    json.dump(new_prompt_set, f, indent=2, ensure_ascii=False)
                print(f"    📄 Created {output_path}")

    print("\n🎉 Done creating all expression prompt sets.")

if __name__ == "__main__":
    create_expression_prompts()
