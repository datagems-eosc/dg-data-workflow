from enum import Enum


class ProfileStatus(Enum):
    JobSubmitted = "Job submitted"
    HeavyProfileReady = "heavy_profile_ready"
    LightProfileReady = "light_profile_ready"