from dataclasses import dataclass

from .infrai_client import EmailResult, InfraiEmailClient
from .models import MatterRequest, plan_delivery


@dataclass(frozen=True)
class MatterEmailResult:
    intake: EmailResult
    signed_document: EmailResult
    followup: EmailResult | None


def send_matter_emails(matter: MatterRequest, client: InfraiEmailClient) -> MatterEmailResult:
    plan = plan_delivery(matter)
    intake = client.send(
        to=matter.client_email,
        subject=plan.intake_subject,
        html=f"<p>Hello {matter.client_name}, we opened matter {matter.matter_id}.</p>",
        request_id=f"{matter.matter_id}:intake",
    )
    signed_document = client.send(
        to=matter.client_email,
        subject=plan.document_subject,
        html=f"<p>Your signed document is ready: {matter.signed_document_name}.</p>",
        request_id=f"{matter.matter_id}:signed-document",
    )
    followup = None
    if plan.followup_subject:
        followup = client.send(
            to=matter.client_email,
            subject=plan.followup_subject,
            html=f"<p>Please review matter {matter.matter_id} within {matter.deadline_days} days.</p>",
            request_id=f"{matter.matter_id}:deadline",
        )
    return MatterEmailResult(intake, signed_document, followup)
