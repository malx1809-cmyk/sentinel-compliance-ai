import os
import time
import json
from dotenv import load_dotenv
from google import genai

load_dotenv()

client = genai.Client(api_key=os.getenv("GEMMA_API_KEY"))

def call_gemma(system_prompt: str, user_prompt: str, max_retries: int = 5):
    wait_time = 2

    for attempt in range(1, max_retries + 1):
        try:
            response = client.models.generate_content(
                model="gemma-4-26b-a4b-it",
                contents=user_prompt,
                config={"system_instruction": system_prompt}
            )

            raw_text = response.text.strip()
            if raw_text.startswith("```"):
                raw_text = raw_text.strip("`")
                raw_text = raw_text.replace("json", "", 1).strip()

            result = json.loads(raw_text)
            time.sleep(1)
            return result

        except json.JSONDecodeError:
            print(f"Could not parse response as JSON on attempt {attempt}. Retrying in {wait_time}s...")
            time.sleep(wait_time)
            wait_time *= 2

        except Exception as e:
            print(f"Error on attempt {attempt}: {type(e).__name__}. Retrying in {wait_time}s...")
            time.sleep(wait_time)
            wait_time *= 2

    print("All retry attempts failed.")
    return None