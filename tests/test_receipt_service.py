from src.models import MatterRequest, plan_delivery


def test_short_deadline_adds_followup_email():
    matter = MatterRequest("MAT-7", "client@example.com", "Sam", "release.pdf", 3)
    plan = plan_delivery(matter)
    assert plan.followup_subject == "Deadline reminder for matter MAT-7"


def test_long_deadline_skips_followup():
    matter = MatterRequest("MAT-8", "client@example.com", "Sam", "release.pdf", 4)
    assert plan_delivery(matter).followup_subject is None
