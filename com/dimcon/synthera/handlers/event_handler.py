import json
import logging
import boto3
from datetime import datetime
from com.dimcon.synthera.utilities.log_handler import LoggerManager
from com.dimcon.synthera.utilities.responses import ResponseBuilder
from com.dimcon.synthera.resources.statement_of_work.meeting_sow_json_store import MeetingSOWJsonStore
from com.dimcon.synthera.services.sow_word_generator import SOWDocumentGenerator

# Setup logger
logger = LoggerManager.setup_logger(__name__, level=logging.DEBUG)

# Optional: S3 bucket if needed
# S3_BUCKET_NAME = "your-s3-bucket-name"

# Optional: Upload function if S3 is needed
# def upload_to_s3(file_path, bucket_name, key):
#     try:
#         s3 = boto3.client("s3")
#         with open(file_path, "rb") as f:
#             s3.upload_fileobj(f, bucket_name, key)
#         logger.info(f"Uploaded to s3://{bucket_name}/{key}")
#     except Exception as e:
#         logger.error(f"Failed to upload to S3: {e}", exc_info=True)
#         raise

def lambda_handler(event, context):
    try:
        # Extract metadata
        sow_ref = event.get("sow_template_reference_number")
        meeting_id = event.get("meeting_id")
        lead_id = event.get("lead_id")
        lead_name = event.get("lead_name")
        org_id = event.get("organization_id")
        org_name = event.get("organization_name")
        created_by = event.get("created_by")

        if not all([sow_ref, meeting_id, lead_id, lead_name, created_by]):
            raise ValueError("Missing required metadata fields in the event.")

        # Step 1: Insert into DB and get new entry
        result = MeetingSOWJsonStore.insert_version(
            sow_ref=sow_ref,
            meeting_id=meeting_id,
            lead_id=lead_id,
            lead_name=lead_name,
            org_id=org_id,
            org_name=org_name,
            payload=event,
            created_by=created_by
        )
        latest_info = MeetingSOWJsonStore.get_latest_by_lead(lead_id)

        if latest_info:
            version = latest_info["version_number"]
            lead_name = latest_info["lead_name"]
    

        # Step 2: Generate Word document
        generator = SOWDocumentGenerator(lead_id=lead_id)
        generator.load_template()
        generator.build_answer_lookup()
        generator.add_metadata()
        generator.add_table_of_contents()
        generator.add_sections()

        # Format safe filename
        file_name = f"SOW_Document_{lead_name}_v{version}.docx"
        # file_path = f"/tmp/{file_name}"
        # generator.save(file_path)

        # Also save locally during dev
        local_path = f"C:/Users/yogie/OneDrive/Documents/GitHub/synthera_sow_generation/{file_name}"
        try:
            generator.save(local_path)
            logger.info(f"Saved document locally: {local_path}")
        except Exception as local_err:
            logger.warning(f"Could not save locally: {local_err}")

        # Optional: Upload to S3
        # s3_key = f"sow_documents/{file_name}"
        # upload_to_s3(file_path, S3_BUCKET_NAME, s3_key)

        return ResponseBuilder.build_response(200, {
            "message": "SOW document created successfully",
            "file_name": file_name,
            "version": version
            # "s3_path": f"s3://{S3_BUCKET_NAME}/{s3_key}" if using S3
        })

    except Exception as e:
        logger.error(f"Unhandled exception in SOW handler: {e}", exc_info=True)
        return ResponseBuilder.build_response(500, {
            "error": str(e)
        })
