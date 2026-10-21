import voluptuous as vol

from homeassistant.config_entries import ConfigFlow, OptionsFlow
from homeassistant.core import callback
from homeassistant.helpers import selector

from .const import (
    CONF_PLANS, CONF_PREP, CONF_SKIP, CONF_TRAVEL,
    DEFAULT_PREP, DEFAULT_SKIP, DEFAULT_TRAVEL, DOMAIN,
)

_MIN = selector.NumberSelector(
    selector.NumberSelectorConfig(min=0, max=300, step=1, unit_of_measurement="min", mode="box")
)


def _schema(hass, d: dict):
    # domyslnie: wszystkie sensory planu Vultron (curr/next, wszystkie dzieci)
    plans = d.get(CONF_PLANS) or [
        s.entity_id for s in hass.states.async_all("sensor")
        if s.entity_id.startswith("sensor.vultron_plan_")
    ]
    return vol.Schema({
        vol.Required(CONF_PLANS, default=plans): selector.EntitySelector(
            selector.EntitySelectorConfig(domain="sensor", multiple=True)
        ),
        vol.Required(CONF_TRAVEL, default=d.get(CONF_TRAVEL, DEFAULT_TRAVEL)): _MIN,
        vol.Required(CONF_PREP, default=d.get(CONF_PREP, DEFAULT_PREP)): _MIN,
        vol.Required(CONF_SKIP, default=d.get(CONF_SKIP, DEFAULT_SKIP)): str,
    })


class VultronAlarmFlow(ConfigFlow, domain=DOMAIN):
    VERSION = 1

    async def async_step_user(self, user_input=None):
        await self.async_set_unique_id(DOMAIN)
        self._abort_if_unique_id_configured()
        if user_input is not None:
            return self.async_create_entry(title="Vultron Alarm Clock", data=user_input)
        return self.async_show_form(step_id="user", data_schema=_schema(self.hass, {}))

    @staticmethod
    @callback
    def async_get_options_flow(entry):
        return VultronAlarmOptions()


class VultronAlarmOptions(OptionsFlow):
    async def async_step_init(self, user_input=None):
        if user_input is not None:
            return self.async_create_entry(data=user_input)
        cur = {**self.config_entry.data, **self.config_entry.options}
        return self.async_show_form(step_id="init", data_schema=_schema(self.hass, cur))
