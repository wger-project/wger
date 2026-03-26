from django.db import migrations

"""
Migration script to copy 'email_verified' column of UserProfile to 'verified' column of EmailAddress table
"""

def migrate_verification_status(apps, schema_editor):
    UserProfile = apps.get_model('core', 'UserProfile')
    EmailAddress = apps.get_model('account', 'EmailAddress')
    
    for profile in UserProfile.objects.all():
        if profile.user.email:
            # Create allauth table using existing userprofile fields
            EmailAddress.objects.get_or_create(
                user=profile.user,
                email=profile.user.email,
                defaults={
                    'verified': profile.email_verified,
                    'primary': True
                }
            )

class Migration(migrations.Migration):
    dependencies = [
        ('core', '0021_add_unit_type_to_repetitionunit'),
        ('account', '0001_initial'),
    ]

    operations = [
        migrations.RunPython(migrate_verification_status),
    ]