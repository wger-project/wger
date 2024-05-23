# Standard Library
from dataclasses import dataclass
from typing import Optional

# wger
from wger.utils.constants import DOWNLOAD_INGREDIENT_WGER


@dataclass
class WgerSettings:
    ALLOW_GUEST_USERS: bool = True
    ALLOW_REGISTRATION: bool = True
    ALLOW_UPLOAD_VIDEOS: bool = False
    DOWNLOAD_INGREDIENTS_FROM: str = DOWNLOAD_INGREDIENT_WGER
    EMAIL_FROM: str = 'wger Workout Manager <wger@example.com>'
    EXERCISE_CACHE_TTL: int = 3600
    MIN_ACCOUNT_AGE_TO_TRUST: int = 21
    SYNC_EXERCISES_CELERY: bool = False
    SYNC_EXERCISE_IMAGES_CELERY: bool = False
    SYNC_EXERCISE_VIDEOS_CELERY: bool = False
    SYNC_INGREDIENTS_CELERY: bool = False
    TWITTER: Optional[str] = None
    MASTODON: Optional[str] = 'https://fosstodon.org/@wger'
    USE_CELERY: bool = False
    USE_RECAPTCHA: bool = False
    WGER_INSTANCE: str = 'https://wger.de'
