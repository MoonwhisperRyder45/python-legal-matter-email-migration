import os
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from src.infrai_client import InfraiEmailClient
from src.models import MatterRequest
from src.receipt_service import send_matter_emails


def main() -> None:
    recipient = os.environ.get("DEMO_EMAIL_TO")
    if not recipient:
        raise SystemExit("DEMO_EMAIL_TO is required")
    matter = MatterRequest(
        matter_id="MAT-1042",
        client_email=recipient,
        client_name="Jordan Lee",
        signed_document_name="engagement-letter.pdf",
        deadline_days=2,
    )
    result = send_matter_emails(matter, InfraiEmailClient())
    print({"intake": result.intake.message_id, "signed_document": result.signed_document.message_id, "followup": result.followup.message_id if result.followup else None})


if __name__ == "__main__":
    main()
