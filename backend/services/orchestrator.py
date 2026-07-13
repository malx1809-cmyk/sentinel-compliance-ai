import sys
import os
import json

sys.path.append(os.path.join(os.path.dirname(__file__), '..'))

from agents.evader_agent import generate_evader_transaction
from agents.detector_agent import detect_transaction_risk
from agents.adjudicator_agent import adjudicate_round

RISK_CATEGORIES = [
    "Structuring cash deposits below PAN-quoting threshold (₹50,000)",
    "Round-tripping funds between related accounts",
    "Dormant account suddenly receiving high-value credit",
    "Multiple small UPI credits from unrelated IDs followed by a sweep-out (mule pattern)"
]

def run_simulation(num_rounds: int = 5):
    evader_feedback = "None yet"
    detector_feedback = "None yet"
    round_history = []

    for round_num in range(1, num_rounds + 1):
        print(f"\n========== ROUND {round_num} ==========")

        risk_category = RISK_CATEGORIES[(round_num - 1) % len(RISK_CATEGORIES)]
        print(f"Target risk category: {risk_category}")

        evader_output = generate_evader_transaction(
            risk_category=risk_category,
            prior_feedback=evader_feedback
        )
        print("\nEvader generated transaction:")
        print(json.dumps(evader_output, indent=2))

        if evader_output is None:
            print(f"Round {round_num}: Evader failed after all retries. Skipping this round.")
            round_history.append({"round": round_num, "outcome": "error", "risk_category": risk_category})
            continue

        detector_output = detect_transaction_risk(
            transaction=evader_output["transaction"],
            prior_feedback=detector_feedback
        )
        print("\nDetector's analysis:")
        print(json.dumps(detector_output, indent=2))

        if detector_output is None:
            print(f"Round {round_num}: Detector failed after all retries. Skipping this round.")
            round_history.append({"round": round_num, "outcome": "error", "risk_category": risk_category})
            continue
        verdict = adjudicate_round(evader_output, detector_output)
        print("\nAdjudicator's verdict:")
        print(json.dumps(verdict, indent=2))

        if verdict is None:
            print(f"Round {round_num} failed after all retries. Skipping this round.")
            round_history.append({
                "round": round_num,
                "outcome": "error",
                "risk_category": risk_category
            })
            continue

        evader_feedback = verdict["feedback_for_evader"]
        detector_feedback = verdict["feedback_for_detector"]

        round_history.append({
            "round": round_num,
            "outcome": verdict["round_outcome"],
            "risk_category": risk_category
        })

    print("\n\n========== SIMULATION SUMMARY ==========")
    caught_count = sum(1 for r in round_history if r["outcome"] == "caught")
    print(f"Total rounds: {num_rounds}")
    print(f"Caught: {caught_count}")
    print(f"Evaded: {num_rounds - caught_count}")
    for r in round_history:
        print(f"Round {r['round']}: {r['outcome']} ({r['risk_category']})")

    return round_history


if __name__ == "__main__":
    run_simulation(num_rounds=5)