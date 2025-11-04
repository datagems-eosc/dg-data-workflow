from enum import Enum


class ProfileStatus(Enum):
    SUBMITTING = "submitting"
    STARTING = "starting"
    LIGHT_PROFILE_READY = "light_profile_ready"
    HEAVY_PROFILES_READY = "heavy_profile_ready"
    CLEANED_UP = "cleaned_up"
