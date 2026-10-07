from dataclasses import dataclass


@dataclass(frozen=True)
class MatterRequest:
    matter_id: str
    client_email: str
    client_name: str
    signed_document_name: str
    deadline_days: int


@dataclass(frozen=True)
class DeliveryPlan:
    intake_subject: str
    document_subject: str
    followup_subject: str | None


def plan_delivery(matter: MatterRequest) -> DeliveryPlan:
    followup = (
        f"Deadline reminder for matter {matter.matter_id}"
        if matter.deadline_days <= 3
        else None
    )
    return DeliveryPlan(
        intake_subject=f"Matter {matter.matter_id} intake received",
        document_subject=f"Signed document: {matter.signed_document_name}",
        followup_subject=followup,
    )
