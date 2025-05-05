import json
import logging
from com.dimcon.synthera.utilities.log_handler import LoggerManager
from com.dimcon.synthera.utilities.responses import ResponseBuilder
from services.json_service import parse_event
from com.dimcon.synthera.utilities.custom_json_encoder import CustomJSONEncoder
from services.db_service import store_data
from services.doc_service import generate_sow
from services.s3_service import upload_document

# Setup logging
LoggerManager.setup_logging()
logger = logging.getLogger(__name__)

def lambda_handler(event, context):
    logger.info("Received event: %s", json.dumps(event, cls=CustomJSONEncoder))

    try:
        # Step 1: Parse the incoming JSON event
        data = parse_event(event)
        if not data:
            logger.error("Failed to parse event: Parsed data is None or invalid.")
            return ResponseBuilder.build_response(
                400, {"error": "Invalid or missing event data. Could not parse the event."}
            )
        logger.info("Event data parsed successfully.")

        # Step 2: Store the extracted data into the database
        db_entry = store_data(data)
        if not db_entry:
            logger.error("Failed to store data into the database.")
            return ResponseBuilder.build_response(
                400, {"error": "Failed to store SOW data into the database."}
            )
        logger.info("Data stored in the database successfully.")

        # Step 3: Generate the Statement of Work document
        sow_doc = generate_sow(db_entry)
        if not sow_doc:
            logger.error("Failed to generate SOW document.")
            return ResponseBuilder.build_response(
                400, {"error": "Failed to generate SOW document."}
            )
        logger.info("SOW document generated successfully.")

        # Step 4: Upload the generated document to Amazon S3
        upload_success = upload_document(sow_doc)
        if not upload_success:
            logger.error("Failed to upload SOW document to S3.")
            return ResponseBuilder.build_response(
                400, {"error": "Failed to upload SOW document to S3."}
            )
        logger.info("SOW document uploaded to S3 successfully.")

        # Final success response
        return ResponseBuilder.build_response(
            200, {"message": "SOW generated and stored successfully."}
        )

    except Exception as e:
        logger.error(f"Error occurred while processing the event: {str(e)}", exc_info=True)
        return ResponseBuilder.build_response(
            500, {"error": f"Internal server error: {str(e)}"}
        )
