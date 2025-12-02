"""Constants for the Azure AI Foundry Conversation integration."""
import logging

DOMAIN = "azure_foundry_conversation"

CONF_ENDPOINT = "endpoint"
CONF_API_KEY = "api_key"
CONF_MODEL_DEPLOYMENT = "model_deployment"
CONF_SYSTEM_PROMPT = "system_prompt"

DEFAULT_SYSTEM_PROMPT = "You are a helpful home assistant. You can control lights, thermostats, and other smart home devices. Keep your responses concise and helpful."
DEFAULT_API_VERSION = "2024-10-21" # A recent stable API version for Azure OpenAI/Foundry
DEFAULT_TEMPERATURE = 0.7
DEFAULT_MAX_TOKENS = 1024

_LOGGER = logging.getLogger(__name__)