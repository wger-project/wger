# Trophy System

The trophy (achievement) system allows users to earn trophies based on
their workout activities.

## Features

- **Multiple Trophy Types**: Time-based, volume-based, count-based,
  sequence-based, date-based, and custom trophies
- **Progressive Trophies**: Show user progress towards earning a trophy
- **Hidden Trophies**: Secret achievements that are revealed only when
  earned
- **Automatic Evaluation**: Trophies are evaluated automatically when
  workout data changes
- **Statistics Tracking**: Denormalized statistics for efficient trophy
  evaluation
- **API Endpoints**: Full REST API for trophy data and progress tracking

## Configuration

### Global Settings

Add to your `settings.py` or `settings_global.py`:

```python
WGER_SETTINGS = {
    # Enable/disable the trophy system globally
    'TROPHIES_ENABLED': True,

    # Number of days of inactivity before skipping trophy evaluation for a user
    'TROPHIES_INACTIVE_USER_DAYS': 30,
}
```

### User Preferences

Users can enable/disable trophies in their profile settings via the
`trophies_enabled` field on `UserProfile`.

## Database Models

### Trophy

Defines an achievement that users can earn.

**Fields:**
- `name`: Trophy name
- `description`: How to earn it
- `trophy_type`: Type (time, volume, count, sequence, date, other)
- `checker_class`: Python class that checks if trophy is earned
  (e.g., 'count_based')
- `checker_params`: JSON parameters for the checker
  (e.g., `{'count': 10}`)
- `is_hidden`: Hidden until earned
- `is_progressive`: Shows progress percentage
- `is_active`: Can be earned (admins can disable)
- `order`: Display order

### UserTrophy

Links users to their earned trophies.

**Fields:**
- `user`: User who earned the trophy
- `trophy`: The trophy earned
- `earned_at`: Timestamp when earned
- `progress`: Progress percentage (0-100)
- `is_notified`: For future notification system

### UserStatistics

Denormalized statistics for efficient trophy checking.

**Fields:**
- `user`: OneToOne with User
- `total_weight_lifted`: Cumulative weight in kg
- `total_workouts`: Number of workout sessions
- `current_streak`: Current consecutive workout days
- `longest_streak`: Longest streak ever achieved
- `earliest_workout_time`: Earliest workout time ever
- `latest_workout_time`: Latest workout time ever
- `weekend_workout_streak`: Consecutive weekends with workouts
- `last_complete_weekend_date`: Last Saturday with both days worked
- `worked_out_jan_1`: Has worked out on any January 1st
- `last_inactive_date`: Last workout before 30+ day gap

## Trophy Checkers

Trophy checkers are Python classes that determine if a user has earned a trophy.

### Available Checkers

1. **count_based**: Check if user reached a count
   - Params: `{'count': 10}`
   - Example: "Complete 10 workouts"

2. **streak**: Check for consecutive day streaks
   - Params: `{'days': 30}`
   - Example: "30-day workout streak"

3. **weekend_warrior**: Check for consecutive complete weekends
   - Params: `{'weekends': 4}`
   - Example: "Work out on Saturday AND Sunday for 4 weekends"

4. **volume**: Check for cumulative weight lifted
   - Params: `{'kg': 5000}`
   - Example: "Lift 5,000 kg total"

5. **time_based**: Check for workout at specific time
   - Params: `{'before': '06:00'}` or `{'after': '21:00'}`
   - Example: "Work out before 6:00 AM"

6. **date_based**: Check for workout on specific date
   - Params: `{'month': 1, 'day': 1}`
   - Example: "Work out on January 1st"

7. **inactivity_return**: Check for return after inactivity
   - Params: `{'inactive_days': 30}`
   - Example: "Return to training after 30 days inactive"

## Management Commands

### Load Trophies

Load the initial set of trophies into the database:

```bash
# Load new trophies (skip existing)
python manage.py load_trophies

# Update existing trophies
python manage.py load_trophies --update

# Verbose output
python manage.py load_trophies -v 2
```

### Evaluate Trophies

Manually trigger trophy evaluation:

```bash
# Evaluate for a specific user
python manage.py evaluate_trophies --user username

# Evaluate a specific trophy for all users
python manage.py evaluate_trophies --trophy 5

# Evaluate all trophies for all active users
python manage.py evaluate_trophies --all

# Force re-evaluation (check already earned trophies)
python manage.py evaluate_trophies --all --force-reevaluate
```

### Recalculate Statistics

Rebuild user statistics from workout history:

```bash
# Recalculate for a specific user
python manage.py recalculate_statistics --user username

# Recalculate for all users
python manage.py recalculate_statistics --all

# Recalculate for active users only
python manage.py recalculate_statistics --all --active-only
```

## API Endpoints

### Trophy Endpoints

```text
GET /api/v2/trophy/
    List all active trophies
    - Hidden trophies excluded unless earned by user

GET /api/v2/trophy/{id}/
    Get specific trophy details

GET /api/v2/trophy/progress/
    Get progress for all trophies (current user)
    - Returns earned status and progress percentage
    - Includes current/target values for progressive trophies
```

### User Trophy Endpoints

```text
GET /api/v2/user-trophy/
    List current user's earned trophies
    - Ordered by earned_at (newest first)

GET /api/v2/user-trophy/{id}/
    Get specific earned trophy details
```

### User Statistics Endpoints

```text
GET /api/v2/user-statistics/
    Get current user's trophy statistics
```

## Adding New Trophies

### Method 1: Using Code (Recommended for new trophy types)

1. **Create a new checker class** (if needed) in `wger/trophies/checkers/`:

```python
# wger/trophies/checkers/my_checker.py
from .base import BaseTrophyChecker

class MyCustomChecker(BaseTrophyChecker):
    def check(self) -> bool:
        # Your logic here
        return True

    def get_progress(self) -> float:
        # Calculate progress 0-100
        return 50.0

    def get_current_value(self):
        return "current"

    def get_target_value(self):
        return "target"
```

2. **Register the checker** in `wger/trophies/checkers/registry.py`:

```python
from .my_checker import MyCustomChecker

class CheckerRegistry:
    _registry: Dict[str, Type[BaseTrophyChecker]] = {
        # ... existing checkers ...
        'my_custom': MyCustomChecker,
    }
```

3. **Add the trophy** via Django admin or shell:

```python
from wger.trophies.models import Trophy

Trophy.objects.create(
    name="My Custom Trophy",
    description="Description of how to earn it",
    trophy_type=Trophy.TYPE_OTHER,
    checker_class='my_custom',
    checker_params={'param1': 'value1'},
    is_hidden=False,
    is_progressive=True,
    order=100,
)
```

### Method 2: Using Existing Checkers

Simply create a new Trophy object with an existing checker:

```python
Trophy.objects.create(
    name="Heavy Lifter",
    description="Lift 10,000 kg total",
    trophy_type=Trophy.TYPE_VOLUME,
    checker_class='volume',
    checker_params={'kg': 10000},
    is_progressive=True,
    order=50,
)
```

### Method 3: Using Fixtures

Create a JSON fixture in `wger/trophies/fixtures/`:

```json
[
  {
    "model": "trophies.trophy",
    "pk": 10,
    "fields": {
      "name": "My Trophy",
      "description": "Description",
      "trophy_type": "count",
      "checker_class": "count_based",
      "checker_params": {"count": 100},
      "is_hidden": false,
      "is_progressive": true,
      "is_active": true,
      "order": 100
    }
  }
]
```

Load with: `python manage.py loaddata my_trophies`

## How It Works

### Signal-Based Updates

When a user logs a workout:

1. `WorkoutSession` or `WorkoutLog` is saved
2. Django signal fires (`post_save`)
3. `UserStatisticsService.increment_workout()` updates statistics
   incrementally
4. `TrophyService.evaluate_all_trophies()` checks for newly earned
   trophies
5. Earned trophies create `UserTrophy` records

### Celery Tasks (Optional)

For async evaluation:

```python
from wger.trophies.tasks import evaluate_user_trophies_task

# Evaluate asynchronously
evaluate_user_trophies_task.delay(user_id)
```

### Performance Considerations

- **Denormalized Statistics**: `UserStatistics` table provides O(1)
  lookups
- **Incremental Updates**: Statistics update incrementally, not full
  recalculation
- **Inactive User Skipping**: Users inactive >30 days are skipped
- **Bulk Operations**: Batch evaluation supports chunking for large
  user sets

## Testing

Run the trophy test suite:

```bash
# All trophy tests
python manage.py test wger.trophies.tests

# Specific test files
python manage.py test wger.trophies.tests.test_models
python manage.py test wger.trophies.tests.test_checkers
python manage.py test wger.trophies.tests.test_services
python manage.py test wger.trophies.tests.test_api
python manage.py test wger.trophies.tests.test_integration
```

## Initial Trophies

The system includes 9 initial trophies:

1. **Beginner**: Complete your first workout
2. **Unstoppable**: Maintain a 30-day workout streak
3. **Weekend Warrior**: Work out on Saturday and Sunday for 4 consecutive
   weekends
4. **Lifter**: Lift a cumulative total of 5,000 kg
5. **Atlas**: Lift a cumulative total of 100,000 kg
6. **Early Bird**: Complete a workout before 6:00 AM
7. **Night Owl**: Complete a workout after 9:00 PM
8. **New Year, New Me**: Work out on January 1st
9. **Phoenix** (Hidden): Return to training after being inactive for
   30 days

Load them with: `python manage.py load_trophies`

## Troubleshooting

### Trophies not being awarded

1. Check if trophy system is enabled: `TROPHIES_ENABLED = True`
2. Check user's profile: `user.userprofile.trophies_enabled`
3. Check user activity: Not inactive >30 days
4. Check trophy is active: `trophy.is_active = True`
5. Recalculate statistics:
   `python manage.py recalculate_statistics --user username`

### Statistics not updating

1. Check signals are connected (should happen automatically)
2. Manually recalculate: `python manage.py recalculate_statistics --all`
3. Check for errors in logs

### Performance issues

1. Add database indexes (already included in migrations)
2. Enable Celery for async evaluation
3. Adjust `TROPHIES_INACTIVE_USER_DAYS` to skip more users
4. Disable trophies for inactive users in bulk

## License

AGPL-3.0 (same as wger Workout Manager)

