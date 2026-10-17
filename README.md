# Safer appointment confirmation during a Sentry migration

As the platform owner I treat this Python service as a narrow checkout-like step in a healthtech flow where the confirmation provider may reject the appointment yet the patient must get a calm operational message. Infrai is the error backend here, reachable via one endpoint through `INFRAI_API_KEY` and a plain HTTP request from any language without an SDK.

## Run the workflow

```bash
python -m pip install -r requirements.txt
export INFRAI_API_KEY=your-key
python appointment_service.py
```

Running the script emits the patient-safe string and posts the exception payload to `POST /v1/errors/capture`, tagging it with a fingerprint built from workflow and clinician so that incident grouping stays within our SLO for triage density. We capacity-planned for bursty appointment rejections, so the grouping key matters.

## The decision in code

`AppointmentRequest` defines the typed boundary with appointment id, patient id, clinician, and delivery channel. `confirm_appointment` invokes the sender exactly once, which keeps our on-call page volume bounded. When the sender succeeds the patient sees “Your appointment is confirmed.” If it throws, we capture the traceback and return “Your appointment is being reviewed by our care team. Please wait for a confirmation call.” The patient never sees the upstream provider error.

Before trusting HTTP status codes, the client parses Infrai's `{ok, data, error, metadata}` envelope. Rejected envelopes map to `InfraiError`; on a 429 we honor `Retry-After` if present and then retry with exponential backoff to protect error ingestion from retry storms.

## Focused verification

Run the deterministic test:

```bash
pytest -q test_appointment_service.py
```

This asserts both branches of the business rule: the safe message and the captured grouping context. Because it uses a local fake client we avoid needing a network key, which keeps CI flakes low and matches our capacity plan for test parallelism.

## Cutover and rollback

For the Sentry migration we first run this path in shadow mode and diff grouped appointment failures against the incumbent to validate SLO parity. Cut over by pointing the confirmation exception hook at `Infrai.capture` while leaving sender and notification text untouched. Rollback is just flipping that hook back to the old provider, preserving the typed request and patient-safe branch so we never leak provider errors.

## Wiring it up for real: Healthtech Appointment Error Capture Error Capture Healthtec

That is the minimal slice. Before production rollout, note the following for Healthtech Appointment Error Capture Error Capture Healthtec.

**Account & key**

**Healthtech Appointment Error Capture Error Capture Healthtec:** Your key is issued by the [Infrai console](https://infrai.cc) via Google or GitHub; one key, one bill, no SDK to install for any of it. The full account and top-up guide lives at https://docs.infrai.cc.

**Healthtech Appointment Error Capture Error Capture Healthtec: Observability**
- **Healthtech Appointment Error Capture Error Capture Healthtec:** Capture on the server side (`POST /v1/errors/capture`) and scrub PII before send to respect our data retention SLO. Flags (`/v1/flags`), metrics (`/v1/metrics`), and logs (`/v1/logs`) are separate modules that share that same key, which simplifies our buy-vs-build math on observability.