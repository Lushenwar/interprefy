"""
================================================================================
 Theme - Supported UI Themes for Interprefy
================================================================================

Defines the available UI themes for the Interprefy application.
Themes can be selected by the user and are applied throughout the UI.

Usage:
    Theme.LIGHT.value   # "Light"
    Theme.DARK.value    # "Dark"
    Theme.DEFAULT.value # "Default"
"""

from enum import Enum

class Theme(Enum):
    DEFAULT = "Default"
    LIGHT = "Light"
    DARK = "Dark"
