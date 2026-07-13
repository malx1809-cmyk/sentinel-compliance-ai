import json
from agents.gemma_client import call_gemma

DETECTOR_SYSTEM_PROMPT = """
You are a financial compliance risk analyst reviewing a single transaction for
an Indian SME, based on RBI KYC and AML red-flag guidelines.

You must reason step by step, then respond ONLY in valid JSON, in this exact format,
with no extra text:

{
  "signals_detected": ["<signal 1>", "<signal 2>"],
  "confidence_per_signal": {"<signal 1>": <0-100>, "<signal 2>": <0-100>},
  "composite_risk_score": <0-100>,
  "flagged": <true or false>,
  "rationale": "<2-3 sentence explanation a human reviewer can act on>"
}

Known red-flag patterns to check for include (but are not limited to):
- Amounts just below the ₹50,000 PAN-quoting threshold
- Amounts just below the ₹10 lakh aggregated cash reporting threshold
- Vague or overly generic transaction descriptions
- Round-number amounts inconsistent with typical business transactions
- Mismatches between stated business type and transaction pattern
- Large credit followed by ~95% of it leaving within minutes or hours (round-tripping)
- A dormant account (inactive 12+ months) suddenly receiving a high-value credit
- Multiple small inward transfers from unrelated senders followed by a single large outward sweep (mule account pattern)
- First-time high-value transfer with no prior transaction history establishing a pattern
- Transaction timing or structuring that suggests deliberate avoidance of a specific reporting threshold
- A transaction between two business entities with no verifiable prior trading relationship, especially for advisory/consulting fees, which are a common vehicle for disguised fund transfers
"""

def detect_transaction_risk(transaction: dict, prior_feedback: str = "None yet"):
    prompt = f"""
Transaction to review (disguise strategy and intent are NOT provided — you must
judge this transaction purely on its own merits, as a real reviewer would):

{json.dumps(transaction, indent=2)}

Feedback from previous rounds (patterns previously missed, pay extra attention to these): {prior_feedback}

Analyze this transaction now, following the JSON format exactly.
"""
    return call_gemma(DETECTOR_SYSTEM_PROMPT, prompt)