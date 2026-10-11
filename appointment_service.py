from dataclasses import dataclass
from typing import Any, Callable
import traceback

from infrai_client import Infrai


@dataclass(frozen=True)
class AppointmentRequest:
    appointment_id: str
    patient_id: str
    clinician: str
    channel: str


@dataclass(frozen=True)
class Notification:
    appointment_id: str
    channel: str
    message: str


def confirm_appointment(
    request: AppointmentRequest,
    send_confirmation: Callable[[AppointmentRequest], None],
    client: Infrai,
) -> Notification:
    """Confirm an appointment, or issue a safe operational message after capture."""
    try:
        send_confirmation(request)
    except Exception as exc:
        client.capture(
            title="appointment confirmation failed",
            message=f"{type(exc).__name__}: {exc}",
            level="error",
            fingerprint=["appointment-confirmation", request.clinician],
            exception=traceback.format_exc(),
            context={"appointment_id": request.appointment_id, "channel": request.channel},
        )
        return Notification(
            request.appointment_id,
            request.channel,
            "Your appointment is being reviewed by our care team. Please wait for a confirmation call.",
        )
    return Notification(request.appointment_id, request.channel, "Your appointment is confirmed.")


def demo() -> None:
    request = AppointmentRequest("apt-1042", "patient-77", "cardiology", "sms")

    def send(_: AppointmentRequest) -> None:
        raise ConnectionError("confirmation provider unavailable")

    result = confirm_appointment(request, send, Infrai())
    print(result.message)


if __name__ == "__main__":
    demo()

