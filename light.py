"""Platform for light integration."""
from __future__ import annotations

import logging
import os

import voluptuous as vol
from typing import Any

# Import the device class from the component that you want to support
import homeassistant.helpers.config_validation as cv
from homeassistant.components.light import (
    ATTR_BRIGHTNESS,
    PLATFORM_SCHEMA,
    LightEntity,
    ATTR_RGB_COLOR,
    COLOR_MODE_RGB,
)
from homeassistant.const import CONF_HOST
from homeassistant.core import HomeAssistant
from homeassistant.helpers.entity_platform import AddEntitiesCallback
from homeassistant.helpers.typing import ConfigType, DiscoveryInfoType

_LOGGER = logging.getLogger(__name__)

# Validation of the user's configuration
PLATFORM_SCHEMA = PLATFORM_SCHEMA.extend({vol.Required(CONF_HOST): cv.string})


def setup_platform(
    hass: HomeAssistant,
    config: ConfigType,
    add_entities: AddEntitiesCallback,
    discovery_info: DiscoveryInfoType | None = None,
) -> None:
    """Set up the Awesome Light platform."""
    # Assign configuration variables.
    # The configuration check takes care they are present.
    mac_address = config[CONF_HOST]

    # Add devices
    add_entities([KeepsmileLight(mac_address)], True)
    return True


def get_color_command(red, green, blue, brightness):
    # brightness broke
    return (
        "5A0001"
        + format(red, "02X")
        + format(green, "02X")
        + format(blue, "02X")
        + "FF00A5"
    )


class KeepsmileLight(LightEntity):
    """Representation of an Awesome Light."""

    def __init__(self, mac_address) -> None:
        """Initialize an AwesomeLight."""
        self._mac = mac_address
        self._brightness = 250
        self._state = False
        self._color = [255, 255, 255]
        self._name = "Keepsmile Light"
        self._attr_supported_color_modes = {COLOR_MODE_RGB}

    @property
    def name(self) -> str:
        """Return the display name of this light."""
        return self._name

    @property
    def brightness(self):
        """Return the brightness of the light.

        This method is optional. Removing it indicates to Home Assistant
        that brightness is not supported for this light.
        """
        return self._brightness

    @property
    def is_on(self) -> bool | None:
        """Return true if light is on."""
        return self._state

    def turn_on(self, **kwargs: Any) -> None:
        """Instruct the light to turn on.

        You can skip the brightness part if your light does not support
        brightness control.
        """
        if ATTR_BRIGHTNESS in kwargs:
            self._brightness = kwargs.get(ATTR_BRIGHTNESS, self.brightness)

        if ATTR_RGB_COLOR in kwargs:
            self._color = kwargs[ATTR_RGB_COLOR]

        if ATTR_BRIGHTNESS in kwargs or ATTR_RGB_COLOR in kwargs:
            command = get_color_command(
                self._color[0], self._color[1], self._color[2], self._brightness
            )
            os.system(
                f"gatttool -b {self._mac} --char-write-req -a 0x0000afd1 -n {command}"
            )

        if not self._state:
            os.system(
                f"gatttool -b {self._mac} --char-write-req -a 0x0000afd1 -n 5BF000B5"
            )
            self._state = True

    def turn_off(self, **kwargs: Any) -> None:
        """Instruct the light to turn off."""
        os.system(f"gatttool -b {self._mac} --char-write-req -a 0x0000afd1 -n 5B0F00B5")
        self._state = False

    def update(self) -> None:
        """Fetch new state data for this light.

        This is the only method that should fetch new data for Home Assistant.
        """
        pass
