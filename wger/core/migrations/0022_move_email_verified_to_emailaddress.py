from django.db import migrations, IntegrityError
from django.db.migrations.state import StateApps


"""
Migration script to copy 'email_verified' column of UserProfile to 'verified' column of EmailAddress table
"""


def migrate_verification_status(apps: StateApps, schema_editor):
    # Bulk-create entries for the allauth table using existing userprofile fields
    UserProfile = apps.get_model('core', 'UserProfile')
    EmailAddress = apps.get_model('account', 'EmailAddress')

    profiles = UserProfile.objects.select_related('user').exclude(user__email='')
    email_addresses = [
        EmailAddress(
            user=profile.user,
            email=profile.user.email,
            verified=profile.email_verified,
            primary=True,
        )
        for profile in profiles
    ]

    EmailAddress.objects.bulk_create(email_addresses, ignore_conflicts=True)


class Migration(migrations.Migration):
    dependencies = [
        ('core', '0021_add_unit_type_to_repetitionunit'),
        ('account', '0001_initial'),
    ]

    operations = [
        migrations.RunPython(migrate_verification_status),
        migrations.RemoveField(
            model_name='userprofile',
            name='email_verified',
        ),
    ]
