import json

# The JSON message as a string
json_message = '''{
    "timestamp": "2024-05-26T07:24:46.827185Z",
    "action": "incident_triggered",
    "target_user": "GitGuardian",
    "incident": {
        "id": 123,
        "date": "2022-08-01T00:00:00.000000Z",
        "detector": {
            "name": "base64_private_key_generic",
            "display_name": "Base64 Generic Private Key",
            "nature": "specific",
            "family": "PrivateKey",
            "detector_group_name": "private_key_generic",
            "detector_group_display_name": "Generic Private Key"
        },
        "secret_revoked": false,
        "validity": "no_checker",
        "occurrence_count": 5,
        "status": "triggered",
        "regression": false,
        "assignee_email": null,
        "severity": "high",
        "ignored_at": null,
        "ignore_reason": null,
        "resolved_at": null
    }
}'''

# Parse the JSON message
data = json.loads(json_message)

# Check if the 'source' key is in the JSON message
source = data.get('source')
message = data.get('message', 'there is an alert')

if source:
    print(f"Command Center, {message}, reported by {source}")
else:
    print(f"Command Center, {message}")
