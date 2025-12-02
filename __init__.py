"""The Azure AI Foundry Conversation component."""
from homeassistant.config_entries import ConfigEntry
from homeassistant.core import HomeAssistant
from homeassistant.const import Platform

from .const import DOMAIN, _LOGGER

async def async_setup_entry(hass: HomeAssistant, entry: ConfigEntry) -> bool:
    """Set up Azure AI Foundry Conversation from a config entry."""
    # This sets up the 'conversation' platform using the data from the config entry
    hass.data.setdefault(DOMAIN, {})[entry.entry_id] = entry.data
    
    # Load the conversation platform
    await hass.config_entries.async_forward_entry_by_domain(entry, Platform.CONVERSATION)

    _LOGGER.debug("Azure AI Foundry Conversation component successfully set up.")
    return True

async def async_unload_entry(hass: HomeAssistant, entry: ConfigEntry) -> bool:
    """Unload a config entry."""
    # Unload the conversation platform
    unload_ok = await hass.config_entries.async_unload_platforms(entry, [Platform.CONVERSATION])
    
    if unload_ok:
        hass.data[DOMAIN].pop(entry.entry_id)
        if not hass.data[DOMAIN]:
            hass.data.pop(DOMAIN)
            
    _LOGGER.debug("Azure AI Foundry Conversation component successfully unloaded.")
    return unload_ok