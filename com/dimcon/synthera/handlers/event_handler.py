import json
import logging
from com.dimcon.synthera.utilities.log_handler import LoggerManager
from com.dimcon.synthera.utilities.responses import ResponseBuilder
from com.dimcon.synthera.utilities.custom_json_encoder import CustomJSONEncoder
from com.dimcon.synthera.resources.statement_of_work.meeting_sow_json_store import MeetingSOWJsonStore

# Setup logging
LoggerManager.setup_logging()
logger = logging.getLogger(__name__)

def lambda_handler(event, context):
    logger.info("Received SOW event: %s", json.dumps(event, cls=CustomJSONEncoder))

    try:
        # Required metadata fields
        sow_ref = event.get("sow_template_reference_number")
        meeting_id = event.get("meeting_id")
        lead_id = event.get("lead_id")
        lead_name = event.get("lead_name")
        org_id = event.get("organization_id")
        org_name = event.get("organization_name")
        created_by = event.get("created_by")

        # Validate input
        if not all([sow_ref, meeting_id, lead_id, lead_name, org_id, org_name, created_by]):
            logger.error("Missing required metadata in SOW JSON event.")
            return ResponseBuilder.build_response(400, {
                "error": "Missing required metadata. Please include meeting_id, lead_id, org_id, and created_by."
            })

        # Store the full payload as versioned entry
        MeetingSOWJsonStore.insert_version(
            sow_ref=sow_ref,
            meeting_id=meeting_id,
            lead_id=lead_id,
            lead_name=lead_name,
            org_id=org_id,
            org_name=org_name,
            payload=event,
            created_by=created_by
        )

        logger.info("SOW JSON stored successfully.")
        return ResponseBuilder.build_response(200, {
            "message": f"SOW JSON stored for lead_id {lead_id} under reference {sow_ref}."
        })

    except Exception as e:
        logger.error(f"Exception during SOW storage: {str(e)}", exc_info=True)
        return ResponseBuilder.build_response(500, {
            "error": f"Internal error: {str(e)}"
        })
