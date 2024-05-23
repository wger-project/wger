# Standard Library
from dataclasses import dataclass
from typing import Optional

# wger
from wger.utils.constants import DOWNLOAD_INGREDIENT_WGER


@dataclass
class WgerSettings:
    allow_guest_users: bool = True
    """
    Allow guest users to access the application.

    If this option is set to true, guest users will be presented with a button
    on the feature page that will generate a guest user for them with some demo
    data.
    """

    allow_registration: bool = True
    """
    Allow users to register for the application.

    Otherwise, only existing users will be able to access the application.
    """

    allow_upload_videos: bool = False
    """
    Allow users to upload exercise videos to the application.
    """

    download_ingredients_from: str = DOWNLOAD_INGREDIENT_WGER
    """
    Source from which to download ingredients.

    Possible values are:

    - wger - `DOWNLOAD_INGREDIENT_WGER`: (default) download ingredients from the
      default wger instance configured in `wger_instance`
    - Open Food Facts - `DOWNLOAD_INGREDIENT_OFF`: download ingredients from Open Food Facts

    """

    email_from: str = 'wger Workout Manager <wger@example.com>'
    """
    Email address from which emails are sent.
    """

    exercise_cache_ttl: int = 3600
    """
    Time to live for cached exercises in seconds.

    Note that at the moment there are a couple more things that are also cached
    for the time set here, most prominently the ingredients
    """

    min_account_age_to_trust: int = 21
    """
    Minimum age of an account, in days, to be considered trusted.

    Trusted accounts are able to add and edit exercises.
    """

    sync_exercises_celery: bool = False
    """
    Whether to sync exercises with the wger API.

    If this is set to true, the application will sync exercises with the default
    wger instance configured in `wger_instance`. A celery task will be created that
    runs at a random time, selected during startup, once a week.
    """

    sync_exercise_images_celery: bool = False
    """
    Whether to sync exercise images with the wger API.

    If this is set to true, the application will sync exercise images with the default
    wger instance configured in `wger_instance`. A celery task will be created that
    runs at a random time, selected during startup, once a week.
    """

    sync_exercise_videos_celery: bool = False
    """
    Whether to sync exercise videos with the wger API.

    If this is set to true, the application will sync exercise videos with the default
    wger instance configured in `wger_instance`. A celery task will be created that
    runs at a random time, selected during startup, once a week.
    """

    sync_ingredients_celery: bool = False
    """
    Whether to sync ingredients with the wger API.

    If this is set to true, the application will sync ingredients with the default
    wger instance configured in `wger_instance`. A celery task will be created that
    runs at a random time, selected during startup, twice per month.
    """

    twitter: Optional[str] = None
    """
    Twitter account of the application.

    This is used to generate a link to the application on Twitter.
    """

    mastodon: Optional[str] = 'https://fosstodon.org/@wger'
    """
    Mastodon instance of the application.

    This is used to generate a link to the application on Mastodon.
    """

    use_celery: bool = False
    """
    Whether to use celery for asynchronous tasks.

    If this is set to true, the application will use celery for asynchronous tasks.
    """

    use_recaptcha: bool = False
    """
    Whether to use recaptcha for registration.

    If this is set to true, the application will use recaptcha for registration.
    """

    wger_instance: str = 'https://wger.de'
    """
    URL of the wger default instance to use for syncing exercises, ingredients and videos.
    """
