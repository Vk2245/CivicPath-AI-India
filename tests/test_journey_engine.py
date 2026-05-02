"""test_journey_engine.py — Journey personalization engine tests."""

from services.journey_engine import generate_timeline_steps, get_state_rules


class TestGetStateRules:
    def test_bihar_rules(self):
        rules = get_state_rules("bihar")
        assert rules["registration_deadline_days"] == 10
        assert rules["voter_id_required"] is True
        assert rules["online_registration"] is True

    def test_up_rules(self):
        rules = get_state_rules("uttar pradesh")
        assert rules["voter_id_required"] is True
        assert rules["same_day_registration"] is False

    def test_unknown_state_defaults(self):
        rules = get_state_rules("unknown_state")
        assert rules["registration_deadline_days"] == 10


class TestGenerateTimeline:
    def test_registered_voter_steps(self):
        steps = generate_timeline_steps("bihar", True, False, "general")
        assert any(s["status"] == "completed" for s in steps)
        assert any(s["title"] == "Cast Your Vote!" for s in steps)

    def test_unregistered_voter_steps(self):
        steps = generate_timeline_steps("bihar", False, True, "general")
        assert any(s["category"] == "registration" and s["status"] == "pending" for s in steps)
        titles = [s["title"] for s in steps]
        assert "Register as a New Voter" in titles

    def test_first_time_voter_extra_step(self):
        steps_first = generate_timeline_steps("bihar", False, True, "general")
        steps_exp = generate_timeline_steps("bihar", False, False, "general")
        assert len(steps_first) > len(steps_exp)

    def test_voter_id_state_includes_id_step(self):
        steps = generate_timeline_steps("uttar pradesh", False, True, "general")
        titles = [s["title"] for s in steps]
        assert "Prepare Your Voter ID (EPIC)" in titles

    def test_step_numbering(self):
        steps = generate_timeline_steps("bihar", False, True, "general")
        for i, step in enumerate(steps):
            assert step["step_number"] == i + 1
            assert "title" in step
            assert "description" in step
            assert "is_critical" in step

    def test_last_step_is_vote(self):
        steps = generate_timeline_steps("bihar", False, True, "general")
        assert "Vote" in steps[-1]["title"]
