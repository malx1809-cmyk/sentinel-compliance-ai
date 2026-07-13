import json
from agents.gemma_client import call_gemma

ADJUDICATOR_SYSTEM_PROMPT = """
You are a neutral compliance audit referee. You are given two things:
1. What a red-team agent (the Evader) was actually trying to hide in a transaction.
2. What a detection agent (the Detector) concluded about that same transaction,
   without seeing the Evader's intent.

Your job is to judge whether the Detector actually caught the real risk the
Evader was hiding, and generate specific, actionable feedback for both agents
to improve next round.

Respond ONLY in valid JSON, in this exact format, with no extra text:

{
  "round_outcome": "caught" or "evaded",
  "reasoning": "<1-2 sentences on why you reached this verdict>",
  "feedback_for_evader": "<specific advice on how to hide this type of risk better next time>",
  "feedback_for_detector": "<specific advice on what to pay attention to next time, especially if it missed something or was right for the wrong reason>"
}

Important: if the Detector flagged the transaction but for a completely different
reason than what the Evader was actually hiding, treat this as "evaded" and explain
the mismatch clearly — a right answer for the wrong reason is not a true catch.
"""

def adjudicate_round(evader_output: dict, detector_output: dict):
    prompt = f"""
What the Evader was trying to hide:
{json.dumps(evader_output, indent=2)}

What the Detector concluded (without seeing the above):
{json.dumps(detector_output, indent=2)}

Judge this round now, following the JSON format exactly.
"""
    return call_gemma(ADJUDICATOR_SYSTEM_PROMPT, prompt)