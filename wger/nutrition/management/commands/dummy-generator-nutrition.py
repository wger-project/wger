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
import datetime
import logging
from random import (
    choice,
    randint,
)
from uuid import uuid4

# Django
from django.contrib.auth.models import User
from django.core.management.base import BaseCommand
from django.utils import timezone

# wger
from wger.nutrition.models import (
    Ingredient,
    LogItem,
    Meal,
    MealItem,
    NutritionPlan,
)


logger = logging.getLogger(__name__)


class Command(BaseCommand):
    """
    Dummy generator for nutritional plans
    """

    help = 'Dummy generator for nutritional plans'

    def add_arguments(self, parser):
        parser.add_argument(
            '--plans',
            action='store',
            default=10,
            dest='nr_plans',
            type=int,
            help='The number of nutritional plans to create per user (default: 10)',
        )
        parser.add_argument(
            '--diary-entries',
            action='store',
            default=20,
            dest='nr_diary_entries',
            type=int,
            help='The number of nutrition logs to create per day (default: 20)',
        )
        parser.add_argument(
            '--diary-dates',
            action='store',
            default=30,
            dest='nr_diary_dates',
            type=int,
            help='Number of dates in which to create logs (default: 30)',
        )
        parser.add_argument(
            '--user-id',
            action='store',
            dest='user_id',
            type=int,
            help='Add only to the specified user-ID (default: all users)',
        )

    def handle(self, **options):
        self.stdout.write(f'** Generating {options["nr_plans"]} dummy nutritional plan(s) per user')

        users = (
            [User.objects.get(pk=options['user_id'])] if options['user_id'] else User.objects.all()
        )
        ingredients = [i for i in Ingredient.objects.order_by('?').all()[:100]]
        meals_per_plan = 4

        for user in users:
            diary_entries = []
            self.stdout.write(f'- processing user {user.username}')

            # Add plan
            for _ in range(0, options['nr_plans']):
                uid = str(uuid4()).split('-')
                start_date = datetime.date.today() - datetime.timedelta(days=randint(0, 100))
                plan = NutritionPlan(
                    description=f'Dummy nutritional plan - {uid[1]}',
                    creation_date=start_date,
                    user=user,
                )
                plan.save()

                if int(options['verbosity']) >= 2:
                    self.stdout.write(f'  created plan {plan.description}')

                # Add meals
                for i in range(0, meals_per_plan):
                    order = 1
                    meal = Meal(
                        plan=plan,
                        order=order,
                        name=f'Dummy meal {i}',
                        time=datetime.time(hour=randint(0, 23), minute=randint(0, 59)),
                    )
                    meal.save()

                    # Add meal items
                    for _ in range(0, randint(1, 5)):
                        meal_item = MealItem(
                            meal=meal,
                            ingredient=choice(ingredients),
                            weight_unit=None,
                            order=order,
                            amount=randint(10, 250),
                        )
                        meal_item.save()
                        order = order + 1

                # Add diary entries
                for _ in range(0, options['nr_diary_dates']):
                    date = timezone.now() - datetime.timedelta(
                        days=randint(0, 100),
                        hours=randint(0, 12),
                        minutes=randint(0, 59),
                    )
                    for _ in range(0, options['nr_diary_entries']):
                        log = LogItem(
                            plan=plan,
                            datetime=date,
                            ingredient=choice(ingredients),
                            weight_unit=None,
                            amount=randint(10, 300),
                        )
                        diary_entries.append(log)

                if int(options['verbosity']) >= 2:
                    self.stdout.write(f'  created {options["nr_diary_dates"]} diary entries')

            LogItem.objects.bulk_create(diary_entries)
