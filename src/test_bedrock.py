import boto3, json

# start a boto3 session with your new profile
session = boto3.Session(profile_name="bedrock-dev")
client = session.client("bedrock-runtime", region_name="us-east-1")

payload = {
    "anthropic_version": "bedrock-2023-05-31",
    "max_tokens": 100,
    "messages": [
        {"role": "user", "content": [{"type": "text", "text": "Hello from Bedrock with SSO!"}]}
    ]
}

resp = client.invoke_model(
    modelId="anthropic.claude-3-5-sonnet-20240620-v1:0",  # adjust if you want a different model
    body=json.dumps(payload),
    contentType="application/json",
    accept="application/json"
)

print(json.loads(resp["body"].read()))
