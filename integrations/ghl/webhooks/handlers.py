"""GHL webhook event handlers — add business logic here."""
import structlog

from .receiver import on_event

log = structlog.get_logger()


@on_event("ContactCreate")
async def handle_contact_created(payload: dict):
    log.info("contact_created", contact_id=payload.get("id"))
    # TODO: sync to Google Sheet, trigger N8N workflow


@on_event("ContactUpdate")
async def handle_contact_updated(payload: dict):
    log.info("contact_updated", contact_id=payload.get("id"))


@on_event("OpportunityCreate")
async def handle_opportunity_created(payload: dict):
    log.info("opportunity_created", opportunity_id=payload.get("id"))


@on_event("OpportunityStatusUpdate")
async def handle_opportunity_stage_change(payload: dict):
    log.info(
        "opportunity_stage_changed",
        opportunity_id=payload.get("id"),
        stage=payload.get("stageId"),
    )
    # TODO: trigger N8N workflow on stage change


@on_event("AppointmentCreate")
async def handle_appointment_created(payload: dict):
    log.info("appointment_created", appointment_id=payload.get("id"))


@on_event("FormSubmit")
async def handle_form_submitted(payload: dict):
    log.info("form_submitted", form_id=payload.get("formId"))
