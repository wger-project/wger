from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('manager', '0024_fill_null_weight_repetitions_units'),
        ('core', '0022_move_email_verified_to_emailaddress'),
    ]

    operations = [
        # SlotEntry: make repetition_unit non-nullable
        migrations.AlterField(
            model_name='slotentry',
            name='repetition_unit',
            field=models.ForeignKey(
                default=1,
                on_delete=django.db.models.deletion.CASCADE,
                to='core.repetitionunit',
            ),
        ),
        # SlotEntry: make weight_unit non-nullable
        migrations.AlterField(
            model_name='slotentry',
            name='weight_unit',
            field=models.ForeignKey(
                default=1,
                on_delete=django.db.models.deletion.CASCADE,
                to='core.weightunit',
                verbose_name='Unit',
            ),
        ),
        # WorkoutLog: make repetition_unit non-nullable
        migrations.AlterField(
            model_name='workoutlog',
            name='repetitions_unit',
            field=models.ForeignKey(
                default=1,
                on_delete=django.db.models.deletion.CASCADE,
                to='core.repetitionunit',
                verbose_name='Repetitions unit',
            ),
        ),
        # WorkoutLog: make weight_unit non-nullable
        migrations.AlterField(
            model_name='workoutlog',
            name='weight_unit',
            field=models.ForeignKey(
                default=1,
                on_delete=django.db.models.deletion.CASCADE,
                to='core.weightunit',
                verbose_name='Weight unit',
            ),
        ),
    ]
