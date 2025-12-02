Azure AI Conversational Service

This repository contains a sample Python application that uses the Azure OpenAI Service (part of the Azure AI Foundry) to handle conversational prompts.

The core logic is located in src/conversation.py.

Requirements

The application requires the openai Python package, configured for the Azure endpoint.

To run this application, you must set the following environment variables:

AZURE_OPENAI_API_KEY: Your Azure OpenAI API key.

AZURE_OPENAI_ENDPOINT: Your Azure OpenAI resource endpoint (e.g., https://your-resource.openai.azure.com/).

AZURE_OPENAI_DEPLOYMENT_NAME: The name of the GPT-3.5 or GPT-4 deployment you created in Azure.