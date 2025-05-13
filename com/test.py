import json
from unittest.mock import MagicMock

# ----------------------
# Mocked database model
# ----------------------
class MeetingSOWJsonStore:
    @classmethod
    def insert_version(cls, sow_ref, meeting_id, lead_id, lead_name, org_id, org_name, payload, created_by):
        print(f"Mock insert_version called with version for lead {lead_id}")
        return True

# ----------------------
# Mocked response builder
# ----------------------
class ResponseBuilder:
    @staticmethod
    def build_response(code, body):
        return {
            "statusCode": code,
            "body": json.dumps(body)
        }

# ----------------------
# Lambda handler under test
# ----------------------
def lambda_handler(event, context):
    try:
        sow_ref = event.get("sow_template_reference_number")
        meeting_id = event.get("meeting_id")
        lead_id = event.get("lead_id")
        lead_name = event.get("lead_name")
        org_id = event.get("organization_id")
        org_name = event.get("organization_name")
        created_by = event.get("created_by")

        if not all([sow_ref, meeting_id, lead_id, lead_name, org_id, org_name, created_by]):
            return ResponseBuilder.build_response(400, {
                "error": "Missing required metadata. Please include meeting_id, lead_id, org_id, and created_by."
            })

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

        return ResponseBuilder.build_response(200, {
            "message": f"SOW JSON stored for lead_id {lead_id} under reference {sow_ref}."
        })

    except Exception as e:
        return ResponseBuilder.build_response(500, {
            "error": f"Internal error: {str(e)}"
        })

# ----------------------
# Test input
# ----------------------
mock_event = {
    "sow_template_reference_number": "SOW-TEST-001",
    "meeting_id": "chime-999",
    "lead_id": 101,
    "lead_name": "Alice Johnson",
    "organization_id": 1,
    "organization_name": "FutureTech Ltd.",
    "created_by": 901,
    "sections": [
        {
            "section_name": "Overview",
            "questionsAndAnswers": [
                {"question_id": "Q1", "question_text": "What is the goal?", "answers_found": ["Automation"], "relavancy_score": 0.95}
            ]
        }
    ]
}

# ----------------------
# Execute test
# ----------------------
if __name__ == "__main__":
    result = lambda_handler(mock_event, None)
    print("Lambda result:", json.dumps(result, indent=2))
