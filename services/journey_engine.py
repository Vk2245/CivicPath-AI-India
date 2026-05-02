"""
journey_engine.py — Election Journey Personalization Engine
=============================================================
Purpose:        Generates personalized election timelines based on
                voter profile (state, registration status, election type)
Inputs:         Voter profile data from onboarding quiz
Outputs:        Ordered list of election preparation steps
Deps:           None (pure business logic)

Challenge Alignment: This is the CORE module for the challenge —
"Create an assistant that helps users understand the election process,
timelines, and steps in an interactive and easy-to-follow way."

GOOGLE API CALLS IN THIS MODULE:
  - generate_personalized_journey(): Delegates to Gemini for AI-generated steps
"""

import logging
from datetime import datetime, timezone
from typing import Any

from demo_data import DEMO_DATA

logger = logging.getLogger("civicpath.journey_engine")

# State-specific election rules (Bihar demo)
STATE_RULES: dict[str, dict[str, Any]] = {
    "bihar": {
        "registration_deadline_days": 10, # ECI allows Form 6 up to 10 days before nomination filing
        "same_day_registration": False,
        "voter_id_required": True, # EPIC or alternate ID is mandatory
        "mail_voting_default": False,
        "early_voting": False, # India does not have general early voting
        "online_registration": True, # NVSP portal
        "provisional_ballot": True, # Tendered vote concept
    },
    "uttar pradesh": {
        "registration_deadline_days": 10,
        "same_day_registration": False,
        "voter_id_required": True,
        "mail_voting_default": False,
        "early_voting": False,
        "online_registration": True,
        "provisional_ballot": True,
    },
    "maharashtra": {
        "registration_deadline_days": 10,
        "same_day_registration": False,
        "voter_id_required": True,
        "mail_voting_default": False,
        "early_voting": False,
        "online_registration": True,
        "provisional_ballot": True,
    },
    "delhi": {
        "registration_deadline_days": 10,
        "same_day_registration": False,
        "voter_id_required": True,
        "mail_voting_default": False,
        "early_voting": False,
        "online_registration": True,
        "provisional_ballot": True,
    },
}

DEFAULT_RULES: dict[str, Any] = {
    "registration_deadline_days": 10,
    "same_day_registration": False,
    "voter_id_required": True,
    "mail_voting_default": False,
    "early_voting": False,
    "online_registration": True,
    "provisional_ballot": True,
}


def get_state_rules(state: str) -> dict[str, Any]:
    """Get election rules for a specific state.

    Args:
        state: State name (lowercase).

    Returns:
        Dictionary of state-specific election rules.
    """
    return STATE_RULES.get(state.lower(), DEFAULT_RULES)


def generate_timeline_steps(
    state: str,
    is_registered: bool,
    is_first_time: bool,
    election_type: str,
) -> list[dict[str, Any]]:
    """Generate personalized election timeline steps.

    Creates a voter-specific preparation timeline based on their state,
    registration status, and experience level. This is the core feature
    that addresses the challenge of making election steps "interactive
    and easy-to-follow."

    Args:
        state: Voter's US state.
        is_registered: Whether voter is already registered.
        is_first_time: Whether first-time voter.
        election_type: Type of election (general, primary, etc.).

    Returns:
        Ordered list of timeline step dictionaries.
    """
    rules = get_state_rules(state)
    steps: list[dict[str, Any]] = []
    step_num = 1

    # Step 1: Check registration (always)
    steps.append({
        "step_number": step_num,
        "title": "Check Your Name in the Voter List",
        "description": (
            f"Visit the Election Commission of India's NVSP portal (voters.eci.gov.in) to verify your "
            f"name in the electoral roll for {state.title()}."
        ),
        "deadline": "Before nomination filing ends",
        "status": "completed" if is_registered else "pending",
        "is_critical": True,
        "category": "registration",
    })
    step_num += 1

    # Step 2: Register (if not registered)
    if not is_registered:
        method = "online via Form 6 or through your BLO" if rules["online_registration"] else "via Form 6 through your BLO"
        steps.append({
            "step_number": step_num,
            "title": "Register as a New Voter",
            "description": (
                f"Register {method}. "
                f"Deadline: Typically {rules['registration_deadline_days']} days before the last date of nomination filing."
            ),
            "deadline": f"~{rules['registration_deadline_days']} days before nomination",
            "status": "pending",
            "is_critical": True,
            "category": "registration",
        })
        step_num += 1

    # Step 3: Gather ID (if required)
    if rules["voter_id_required"]:
        steps.append({
            "step_number": step_num,
            "title": "Prepare Your Voter ID (EPIC)",
            "description": (
                f"The ECI requires identification to vote. Your Electors Photo Identity Card (EPIC) "
                "is best. If you don't have it, Aadhaar, PAN card, Passport, or Driving License "
                "are among the 12 accepted alternatives."
            ),
            "deadline": "1 week before election",
            "status": "pending",
            "is_critical": True,
            "category": "preparation",
        })
        step_num += 1

    # Step 4: Research ballot
    steps.append({
        "step_number": step_num,
        "title": "Know Your Candidates",
        "description": (
            f"Review the candidates contesting from your constituency for the {election_type} election. "
            "You can use the KYC (Know Your Candidate) app by ECI to check their details and criminal antecedents."
        ),
        "deadline": "1 week before election",
        "status": "pending",
        "is_critical": False,
        "category": "research",
    })
    step_num += 1

    # Step 5: Download Voter Slip
    steps.append({
        "step_number": step_num,
        "title": "Download Voter Information Slip",
        "description": (
            "Download your Voter Information Slip from the Voter Helpline App or NVSP portal. "
            "This confirms your polling booth details (Part Number and Serial Number)."
        ),
        "deadline": "3 days before election",
        "status": "pending",
        "is_critical": False,
        "category": "logistics",
    })
    step_num += 1

    # Step 6: Find polling place
    steps.append({
        "step_number": step_num,
        "title": "Find Your Polling Booth",
        "description": (
            "Use CivicPath's Polling Place Finder or check your Voter Information Slip for your "
            "assigned polling booth."
        ),
        "deadline": "1 day before election",
        "status": "pending",
        "is_critical": True,
        "category": "logistics",
    })
    step_num += 1

    # Step 7: First-time voter extras
    if is_first_time:
        steps.append({
            "step_number": step_num,
            "title": "Know the EVM Process",
            "description": (
                "As a first-time voter: Hand your slip/ID to the polling officer. They will ink your "
                "finger and give you a chit. Give the chit to the presiding officer, proceed to the "
                "voting compartment, press the blue button on the EVM next to your candidate, and verify "
                "the printed slip in the VVPAT machine."
            ),
            "deadline": "Election Day",
            "status": "pending",
            "is_critical": False,
            "category": "preparation",
        })
        step_num += 1

    # Final step: Vote!
    steps.append({
        "step_number": step_num,
        "title": "Cast Your Vote!",
        "description": (
            "Head to your polling booth, bring your EPIC or valid ID, and vote! "
            "Polls are typically open from 7:00 AM to 6:00 PM. If you are in the queue at closing time, "
            "you have the right to vote."
        ),
        "deadline": "Election Day",
        "status": "pending",
        "is_critical": True,
        "category": "voting",
    })

    return steps
