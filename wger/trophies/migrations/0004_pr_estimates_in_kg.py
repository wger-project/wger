from django.db import migrations
from django.db.migrations.state import StateApps

# Values of wger.manager.consts.WEIGHT_UNIT_LB and AbstractWeight.LB_IN_KG
WEIGHT_UNIT_LB = 2
LB_IN_KG = 0.45359237


def convert_pr_estimates_to_kg(apps: StateApps, schema_editor):
    """
    Personal record estimates of lb logs were stored in lb, the checker now
    compares in kg
    """
    UserTrophy = apps.get_model('trophies', 'UserTrophy')

    user_trophies = UserTrophy.objects.filter(
        trophy__checker_class='personal_record',
        context_data__weight_unit_id=WEIGHT_UNIT_LB,
    )
    for user_trophy in user_trophies.iterator():
        context = user_trophy.context_data
        estimate = context.get('one_rep_max_estimate')
        if not isinstance(estimate, (int, float)):
            continue

        context['one_rep_max_estimate'] = round(estimate * LB_IN_KG, 2)
        user_trophy.context_data = context
        user_trophy.save(update_fields=['context_data'])


class Migration(migrations.Migration):
    dependencies = [
        ('trophies', '0003_migrate_context_data_uuids'),
    ]

    operations = [
        migrations.RunPython(convert_pr_estimates_to_kg, migrations.RunPython.noop),
    ]
