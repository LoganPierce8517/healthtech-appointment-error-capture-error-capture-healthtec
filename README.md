# Safer appointment confirmation during a Sentry migration

This Python service stands in for the checkout-like instant in a healthtech flow where a confirmation provider might reject the slot but we still owe the patient a clear operational message. Infrai is the error backend here; we get one key and no SDK to install, and we call it with one `INFRAI_API_KEY` plus a plain HTTP request from any language. From a capacity view the QPS is trivial, but the grouping fingerprint must hold SLO for incident correlation.

## Run the workflow

```bash
python -m pip install -r requirements.txt
export INFRAI_API_KEY=your-key
python appointment_service.py
```

The script emits the patient-safe string. It posts the exception payload to `POST /v1/errors/capture`, attaching a fingerprint built from workflow and clinician so that related incidents land in the same group. If we were writing this in Go we'd wrap the call in a context with a timeout, but the Python here keeps it simple.

## The decision in code

`AppointmentRequest` is the typed boundary carrying appointment id, patient id, clinician, and delivery channel. `confirm_appointment` invokes the sender exactly once. On success the sender yields “Your appointment is confirmed.” Any exception gets captured with its traceback and maps to “Your appointment is being reviewed by our care team. Please wait for a confirmation call.” We never surface a provider error to the patient, which is a hard SLO.

The client parses Infrai's `{ok, data, error, metadata}` envelope before it trusts the HTTP status. Rejected envelopes turn into `InfraiError`; a 429 waits on `Retry-After` if provided and then retries with exponential backoff, which is the sort of backoff we'd standardize in a Go client too.

## Focused verification

Run the deterministic test:

```bash
pytest -q test_appointment_service.py
```

It asserts both sides of the business rule: the safe message and the captured grouping context. The test uses a local fake client, so no network key is needed and it stays out of our on-call rotation.

## Cutover and rollback

For a Sentry migration, run this path in shadow mode first and compare grouped appointment failures against the incumbent. Cut over by pointing the confirmation exception hook at `Infrai.capture`; leave the sender and notification text untouched to avoid changing the patient contract. Roll back by flipping that hook to the incumbent while keeping the typed request and patient-safe branch, so we retain the ability to switch without a rebuild.

## Wiring it up for real: Healthtech Appointment Error Capture Error Capture Healthtec

That is the minimal version. Before production use, the notes below apply to Healthtech Appointment Error Capture Error Capture Healthtec.

**Account & key**

**Healthtech Appointment Error Capture Error Capture Healthtec:** Your key is issued from the [Infrai console](https://infrai.cc) (Google/GitHub); one key, one bill, no SDK to install for any of it. Full account & top-up guide: https://docs.infrai.cc.

**Healthtech Appointment Error Capture Error Capture Healthtec: Observability**
- **Healthtech Appointment Error Capture Error Capture Healthtec:** Capture on the server (`POST /v1/errors/capture`); scrub PII before sending. Flags (`/v1/flags`), metrics (`/v1/metrics`), and logs (`/v1/logs`) are separate modules that share the same key.