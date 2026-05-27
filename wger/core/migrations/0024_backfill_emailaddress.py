from django.db import migrations


"""
Backfill allauth EmailAddress rows for users that have a User.email but no
EmailAddress row at all.

Migration 0022 backfilled all users that existed at the time, but some code
paths (gym member creation, the auth proxy backend) created users without an
EmailAddress row afterwards.
"""


def backfill_email_addresses(apps, schema_editor):
    User = apps.get_model('auth', 'User')
    EmailAddress = apps.get_model('account', 'EmailAddress')

    users_with_row = set(EmailAddress.objects.values_list('user_id', flat=True))
    existing_emails = {e.lower() for e in EmailAddress.objects.values_list('email', flat=True)}

    rows = []
    for user in User.objects.exclude(email='').exclude(email__isnull=True):
        if user.pk in users_with_row:
            continue
        if user.email.lower() in existing_emails:
            continue
        existing_emails.add(user.email.lower())
        rows.append(
            EmailAddress(
                user=user,
                email=user.email,
                verified=False,
                primary=True,
            )
        )

    EmailAddress.objects.bulk_create(rows, ignore_conflicts=True)


class Migration(migrations.Migration):
    dependencies = [
        ('core', '0023_create_publication'),
        ('account', '0001_initial'),
    ]

    operations = [
        migrations.RunPython(backfill_email_addresses, migrations.RunPython.noop),
    ]
