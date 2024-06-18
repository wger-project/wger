# This file is part of wger Workout Manager.
#
# wger Workout Manager is free software: you can redistribute it and/or modify
# it under the terms of the GNU Affero General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# wger Workout Manager is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU Affero General Public License

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
    """

    ingredient_cache_ttl: int = 604800
    """
    Time to live for cached ingredients in seconds. Default is one week.
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

    sync_off_daily_delta_celery: bool = False
    """
    Whether to sync the Open Food Facts deltas to the databse
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

    def __setitem__(self, key, value):
        """For compatibility purposes, accept the old dictionary syntax"""
        setattr(self, key.lower(), value)

    def __getitem__(self, item):
        """For compatibility purposes, accept the old dictionary syntax"""
        return getattr(self, item.lower())
