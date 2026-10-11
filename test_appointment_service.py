from appointment_service import AppointmentRequest, Notification, confirm_appointment


class FakeInfrai:
    def __init__(self):
        self.payload = None

    def capture(self, **payload):
        self.payload = payload
        return {"event_id": "evt-test"}


def test_failed_confirmation_is_patient_safe_and_captured():
    client = FakeInfrai()
    request = AppointmentRequest("apt-1", "patient-1", "cardiology", "sms")

    def failing_sender(_):
        raise ValueError("provider rejected request")

    result = confirm_appointment(request, failing_sender, client)

    assert isinstance(result, Notification)
    assert "care team" in result.message
    assert client.payload["fingerprint"] == ["appointment-confirmation", "cardiology"]
    assert client.payload["context"]["appointment_id"] == "apt-1"

