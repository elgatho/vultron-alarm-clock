from datetime import timedelta

from homeassistant.components.sensor import SensorDeviceClass, SensorEntity
from homeassistant.core import callback
from homeassistant.helpers.event import async_track_state_change_event, async_track_time_change
from homeassistant.util import dt as dt_util

from .const import CONF_PLANS, CONF_PREP, CONF_SKIP, CONF_TRAVEL, DOMAIN
from .logic import compute_alarm


async def async_setup_entry(hass, entry, async_add_entities):
    async_add_entities([VultronAlarmSensor(entry)])


class VultronAlarmSensor(SensorEntity):
    _attr_has_entity_name = True
    _attr_translation_key = "alarm"
    _attr_icon = "mdi:alarm"
    _attr_device_class = SensorDeviceClass.TIMESTAMP
    _attr_should_poll = False

    def __init__(self, entry):
        self._cfg = {**entry.data, **entry.options}
        self._attr_unique_id = entry.entry_id
        self._attr_device_info = {"identifiers": {(DOMAIN, entry.entry_id)}, "name": "Vultron Alarm Clock"}

    async def async_added_to_hass(self):
        self.async_on_remove(
            async_track_state_change_event(self.hass, self._cfg[CONF_PLANS], self._changed)
        )
        # przeskok na nowy dzien ("jutro" sie zmienia o polnocy)
        self.async_on_remove(
            async_track_time_change(self.hass, self._changed, hour=0, minute=0, second=5)
        )
        self._recompute()

    @callback
    def _changed(self, *_):
        self._recompute()
        self.async_write_ha_state()

    def _recompute(self):
        target = dt_util.now().date() + timedelta(days=1)
        plans = [
            s.attributes
            for e in self._cfg[CONF_PLANS]
            if (s := self.hass.states.get(e)) is not None
        ]
        skip = {x.strip().upper() for x in self._cfg[CONF_SKIP].split(",") if x.strip()}
        when, info = compute_alarm(
            plans, target, int(self._cfg[CONF_TRAVEL]), int(self._cfg[CONF_PREP]), skip
        )
        self._attr_native_value = (
            when.replace(tzinfo=dt_util.DEFAULT_TIME_ZONE) if when else None
        )
        self._attr_extra_state_attributes = {
            "date": target.isoformat(),
            "alarm_time": when.strftime("%H:%M") if when else None,  # lokalne HH:MM dla iOS
            "first_lesson": info if when else None,
            "reason": None if when else info,  # weekend / dzien_wolny / brak_lekcji
            "travel_minutes": int(self._cfg[CONF_TRAVEL]),
            "prep_minutes": int(self._cfg[CONF_PREP]),
        }
