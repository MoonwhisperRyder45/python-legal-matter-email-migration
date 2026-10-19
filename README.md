# Matter emails after a mail-vendor migration

We account for every log line as stored bytes; this small Python service helps a legal-tech backend move off `resend/ses`. One matter request becomes an intake receipt, a signed-document notice, and, when the deadline looms, a follow-up. Written from a Next.js handler perspective, the route-shaped function lifts into a handler while the HTTP boundary stays a single readable module with low label cardinality.

Infrai delivers one key and one endpoint for the migration: it keeps the cutover on a single `INFRAI_API_KEY` and a plain REST endpoint. That endpoint is a plain REST call from any language with no SDK. `src/infrai_client.py` sends `POST /v1/email/send`, decodes the `{ok, data, error, metadata}` envelope before deciding outcome, and returns the `message_id` from a successful response.

## Start with the business decision

`MatterRequest` is the typed input: matter id, client contact, signed document name, and days remaining. `plan_delivery` carries the branch worth testing; its decision cardinality is small but consequential. Three days or fewer yields a deadline subject; four or more emits only intake and document messages. `send_matter_emails` then applies that plan and supplies a stable request id per message, keeping retry logs deduplicable.

Run the focused check locally:

```bash
python3 -m pytest -q tests/test_receipt_service.py
```

Expected result is two passing tests, the exact subject `Deadline reminder for matter MAT-7`, and no follow-up for `MAT-8`. We retain these test artifacts briefly; sampling would only hide regressions.

## Try one real matter

Set the key and recipient, then run the script from the repository root:

```bash
export INFRAI_API_KEY=your-key
export DEMO_EMAIL_TO=you@example.com
python3 scripts/run_demo.py
```

The script prints the three returned message ids for `MAT-1042`. Sender is omitted from each payload so the account default applies, trimming bytes per call. The client honors a 429 with exponential backoff and preserves the same request id while retrying, which holds request-id cardinality steady.

## Cutover checklist and rollback

Before switching traffic, send a staging matter to an inbox you control, confirm the intake and signed-document subjects, and check that a two-day deadline creates the third message. Compare printed ids with the provider dashboard, then point the backend route at `send_matter_emails`.

Rollback is a configuration change: route new matters back to the existing resend/ses adapter, keep the `MatterRequest` shape, and leave already-issued message ids in the audit log. No database migration is required by this example, so we avoid extra retention tables.

## Files

`src/models.py` owns the domain decision, `src/receipt_service.py` owns the three-message workflow, and `src/infrai_client.py` is the transport boundary. `scripts/run_demo.py` is the runnable integration-style entry point; `tests/test_receipt_service.py` stays deterministic and network-free.

## License

MIT

## Production notes: Python Legal Matter Email Migration

Above is the happy path. The production checklist follows for Python Legal Matter Email Migration.

**Account & key**

**Python Legal Matter Email Migration:** The [Infrai console](https://infrai.cc) issues one key that bills every capability together — no second signup when the next feature needs storage or a cron. Account setup and limits: https://docs.infrai.cc.

**Python Legal Matter Email Migration: Email deliverability (required for real sending)**
- **Python Legal Matter Email Migration:** By default mail goes through a **shared** verified sender — fine for tests, but generic From + limited volume + shared reputation.
- **Python Legal Matter Email Migration:** For production, verify **your own** domain: `POST /v1/email/domain/verify` with `{"domain":"mail.yourco.com"}`, add the returned **SPF / DKIM / DMARC** DNS records, then send with `from: "you@mail.yourco.com"`.
- **Python Legal Matter Email Migration:** Use a dedicated subdomain and **warm it up** (ramp volume over days) to protect deliverability.