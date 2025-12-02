"""The Azure AI Foundry Conversation component."""
import json
import http
from typing import Literal

from aiohttp import ClientError, ClientResponseError

from homeassistant.core import HomeAssistant
from homeassistant.components.conversation import ConversationEntity, ConversationResult, Abstract==Agent
from homeassistant.config_entries import ConfigEntry
from homeassistant.helpers.aiohttp_client import async_get_clientsession
from homeassistant.helpers import intent
from homeassistant.util import ulid

from .const import (
    DOMAIN,
    CONF_ENDPOINT,
    CONF_API_KEY,
    CONF_MODEL_DEPLOYMENT,
    CONF_SYSTEM_PROMPT,
    DEFAULT_API_VERSION,
    DEFAULT_TEMPERATURE,
    DEFAULT_MAX_TOKENS,
    _LOGGER,
)

# Base path for the Azure OpenAI compatible API on Foundry deployments
AZURE_OPENAI_PATH = "/openai/deployments/{deployment_name}/chat/completions"

class AzureFoundryConversation(ConversationEntity):
    """Azure AI Foundry Conversation Agent."""

    def __init__(self, hass: HomeAssistant, entry: ConfigEntry):
        """Initialize the conversation agent."""
        self.hass = hass
        self.entry = entry
        self.name = entry.title
        self.agent = AzureFoundryAgent(hass, entry.data)

    @property
    def unique_id(self):
        """Return a unique ID for the agent."""
        return self.entry.entry_id

    @property
    def supported_features(self) -> intent.IntentSupportedFeatures:
        """Return the supported features."""
        return intent.IntentSupportedFeatures.standard_features

    async def async_process(self, user_input: intent.IntentProcessText) -> ConversationResult:
        """Process a sentence."""
        return await self.agent.async_process(user_input)


class AzureFoundryAgent(AbstractAgent):
    """The actual Azure AI Foundry LLM agent."""

    def __init__(self, hass: HomeAssistant, config: dict):
        """Initialize the agent."""
        self.hass = hass
        self.config = config
        self.session = async_get_clientsession(hass)
        self.history = {} # Simple in-memory history, keyed by conversation ID

    @property
    def supported_languages(self) -> list[str] | Literal["*"]:
        """Return a list of supported languages."""
        return "*"

    async def async_process(self, user_input: intent.IntentProcessText) -> ConversationResult:
        """Process a sentence."""
        conversation_id = user_input.conversation_id if user_input.conversation_id else ulid.ulid()
        
        # Get history or initialize
        messages = self.history.get(conversation_id, [])

        # Always include the system prompt at the start
        system_prompt = self.config.get(CONF_SYSTEM_PROMPT)
        if not messages or messages[0]["role"] != "system":
            messages.insert(0, {"role": "system", "content": system_prompt})

        # Add user's new message
        messages.append({"role": "user", "content": user_input.text})

        # Construct the API request
        endpoint = self.config[CONF_ENDPOINT]
        api_key = self.config[CONF_API_KEY]
        deployment_name = self.config[CONF_MODEL_DEPLOYMENT]

        url = f"{endpoint}{AZURE_OPENAI_PATH.format(deployment_name=deployment_name)}?api-version={DEFAULT_API_VERSION}"
        
        headers = {
            "Content-Type": "application/json",
            "api-key": api_key, # Use the Azure AI Foundry API key
        }
        
        payload = {
            "messages": messages,
            "temperature": DEFAULT_TEMPERATURE,
            "max_tokens": DEFAULT_MAX_TOKENS,
        }

        try:
            # Make the asynchronous API call
            async with self.session.post(url, headers=headers, json=payload) as response:
                response.raise_for_status() # Raise exception for bad status codes (4xx or 5xx)
                
                response_data = await response.json()
                
                if not response_data or not response_data.get("choices"):
                    _LOGGER.error("Azure AI Foundry response was empty or lacked choices: %s", response_data)
                    text = "I received an empty response from the AI model."
                else:
                    # Extract the response text
                    ai_response_text = response_data["choices"][0]["message"]["content"]
                    text = ai_response_text
                    
                    # Add AI response to history for next turn
                    messages.append({"role": "assistant", "content": ai_response_text})
                    self.history[conversation_id] = messages
                    
        except ClientResponseError as err:
            if err.status == http.HTTPStatus.UNAUTHORIZED:
                _LOGGER.error("Azure AI Foundry Authorization failed: Check API Key and Endpoint/Deployment Name.")
                text = "Authentication failed. Please check your Azure AI Foundry configuration."
            else:
                _LOGGER.error("Azure AI Foundry API request failed with status %d: %s", err.status, err.message)
                text = f"An API error occurred: Status {err.status}."
        except ClientError as err:
            _LOGGER.error("Network or Client Error when connecting to Azure AI Foundry: %s", err)
            text = "Could not connect to the Azure AI Foundry endpoint. Check your network connection and URL."
        except Exception as err:
            _LOGGER.exception("An unexpected error occurred during API call: %s", err)
            text = "An unexpected error occurred while processing your request."

        # Return the final result
        return ConversationResult(
            response=intent.IntentResponse(
                speech={
                    "plain": {"speech": text},
                },
                card={
                    "title": "Azure AI Foundry Response",
                    "content": text,
                },
            ),
            conversation_id=conversation_id,
        )

# Register the conversation component
async def async_setup_entry(hass: HomeAssistant, entry: ConfigEntry) -> None:
    """Set up the conversation entry."""
    hass.data[DOMAIN][entry.entry_id] = AzureFoundryConversation(hass, entry)