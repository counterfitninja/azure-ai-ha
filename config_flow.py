"""Config flow for Azure AI Foundry Conversation."""
import voluptuous as vol

from homeassistant import config_entries
from homeassistant.core import HomeAssistant
from homeassistant.data_entry_flow import FlowResult
from homeassistant.const import CONF_API_KEY

from .const import (
    DOMAIN,
    CONF_ENDPOINT,
    CONF_MODEL_DEPLOYMENT,
    CONF_SYSTEM_PROMPT,
    DEFAULT_SYSTEM_PROMPT,
    _LOGGER,
)

STEP_USER_DATA_SCHEMA = vol.Schema({
    vol.Required(CONF_ENDPOINT): str,
    vol.Required(CONF_API_KEY): str,
    vol.Required(CONF_MODEL_DEPLOYMENT): str,
    vol.Optional(CONF_SYSTEM_PROMPT, default=DEFAULT_SYSTEM_PROMPT): str,
})

class AzureFoundryConfigFlow(config_entries.ConfigFlow, domain=DOMAIN):
    """Handle a config flow for Azure AI Foundry Conversation."""

    VERSION = 1

    async def async_step_user(self, user_input=None) -> FlowResult:
        """Handle the initial step."""
        errors = {}

        if user_input is not None:
            # Basic validation of the endpoint URL format (cannot guarantee it works)
            if not (user_input[CONF_ENDPOINT].startswith("https://") and 
                    "services.ai.azure.com" in user_input[CONF_ENDPOINT]):
                errors["base"] = "invalid_endpoint"
            
            # Since we cannot easily test the API key without making a full request, 
            # we rely on the user to provide correct credentials.
            # A real connection test would be added here in a production integration.

            if not errors:
                return self.async_create_entry(
                    title="Azure AI Foundry: " + user_input[CONF_MODEL_DEPLOYMENT],
                    data=user_input,
                )

        return self.async_show_form(
            step_id="user",
            data_schema=STEP_USER_DATA_SCHEMA,
            errors=errors,
        )