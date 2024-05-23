# Standard Library
from dataclasses import dataclass
from typing import Optional

# wger
from wger.utils.constants import DOWNLOAD_INGREDIENT_WGER


@dataclass
class WgerSettings:
    allow_guest_users: bool = True
    allow_registration: bool = True
    allow_upload_videos: bool = False
    download_ingredients_from: str = DOWNLOAD_INGREDIENT_WGER
    email_from: str = 'wger Workout Manager <wger@example.com>'
    exercise_cache_ttl: int = 3600
    min_account_age_to_trust: int = 21
    sync_exercises_celery: bool = False
    sync_exercise_images_celery: bool = False
    sync_exercise_videos_celery: bool = False
    sync_ingredients_celery: bool = False
    twitter: Optional[str] = None
    mastodon: Optional[str] = 'https://fosstodon.org/@wger'
    use_celery: bool = False
    use_recaptcha: bool = False
    wger_instance: str = 'https://wger.de'
