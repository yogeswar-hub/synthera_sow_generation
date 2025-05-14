import json
from com.dimcon.synthera.handlers.event_handler import lambda_handler

if __name__ == "__main__":
    with open("test_event_2.json", "r") as f:
        event = json.load(f)

    context = {}  # mock context for Lambda
    result = lambda_handler(event, context)
    print(json.dumps(result, indent=2))
