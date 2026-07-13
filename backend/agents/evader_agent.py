from agents.gemma_client import call_gemma

EVADER_SYSTEM_PROMPT = """
You are a red-team compliance analyst helping test a fraud detection system.
Your job is to generate a realistic SME bank transaction that embeds a specific
type of financial risk, while making it look as legitimate as possible.

You must respond ONLY in valid JSON, in this exact format, with no extra text:

{
  "transaction": {
    "amount": <number>,
    "currency": "INR",
    "description": "<short transaction description>",
    "sender": "<sender name>",
    "receiver": "<receiver name>"
  },
  "disguise_strategy": "<one sentence explaining how this hides the risk>",
  "target_risk_category": "<the risk category this represents>",
  "concealment_confidence": <number from 0 to 100>
}
"""

def generate_evader_transaction(risk_category: str, prior_feedback: str = "None yet"):
    prompt = f"""
Risk category to embed: {risk_category}
Feedback from previous rounds (what got caught before, avoid repeating this): {prior_feedback}

Generate one transaction now, following the JSON format exactly.
"""
    return call_gemma(EVADER_SYSTEM_PROMPT, prompt)