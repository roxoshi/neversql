# Use the Converse API to send a text message to Mistral 7B Instruct.

import boto3
from botocore.exceptions import ClientError
from typing import Optional, Dict
from constants import BEDROCK_DEFAULT_MODEL

DEFAULT_MODEL_ID = 'meta.llama3-8b-instruct-v1:0'
DEFAULT_MODEL_KWARGS = {
    "max_gen_len": 1024,
    "temperature": 0,
    "top_p": 0.7
}
# Create a Bedrock Runtime client in the AWS Region you want to use.
client = boto3.client("bedrock-runtime", region_name="us-east-1")
class BedrockLLM:
    def __init__(self, model_id: Optional[str] = None, model_kwargs: Optional[Dict] = None):
        self.model_id = model_id or BEDROCK_DEFAULT_MODEL
        self.model_kwargs = model_kwargs or DEFAULT_MODEL_KWARGS
    
    # Set the model ID, e.g., Titan Text Premier.
    def llm(self, prompt: str):
        # Start a conversation with the user message.
        user_message = f"""[INST]{prompt}[/INST]"""
        conversation = [
            {
                "role": "user",
                "content": [{"text": user_message}],
            }
        ]

        try:
            # Send the message to the model, using a basic inference configuration.
            response = client.converse(
                modelId=self.model_id,
                messages=conversation,
                inferenceConfig={"maxTokens":400,"temperature":0.7,"topP":0.7},
            )

            # Extract and print the response text.
            response_text = response["output"]["message"]["content"][0]["text"]
            print(response_text)

        except (ClientError, Exception) as e:
            print(f"ERROR: Can't invoke '{self.model_id}'. Reason: {e}")
            exit(1)


