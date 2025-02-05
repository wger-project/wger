import json
import os
from django.core.management.base import BaseCommand
from django.db import transaction, connection, IntegrityError
from django.db.utils import OperationalError
from django.conf import settings
from wger.core.models import Language  # Ensure you have the correct model import

class Command(BaseCommand):
    """
    Synchronize core_language table with fixture data from languages.json
    """

    help = (
        'Synchronize core_language table with fixture data from languages.json'
        'This is needed if a language has been deleted from the interface'
        'and a sync of the exercises is done.'
    )

    def handle(self, *args, **kwargs):
        try:
            # Define the standard path to the languages.json file
            json_file_path = os.path.join('wger', 'core', 'fixtures', 'languages.json')

            # Check if the file exists
            if not os.path.exists(json_file_path):
                self.stdout.write(self.style.ERROR(f'Fixture file not found: {json_file_path}'))
                return

            # Load JSON data from languages.json
            self.stdout.write('Loading data from languages.json')
            with open(json_file_path, 'r', encoding='utf-8') as file:
                json_data = json.load(file)

            self.stdout.write(f'Successfully loaded JSON data. Records count: {len(json_data)}')

            with transaction.atomic():
                # Create a temporary table
                self.stdout.write('Creating temporary table')
                cursor = connection.cursor()

                try:
                    cursor.execute("""
                        CREATE TEMPORARY TABLE temp_core_language (
                            id INTEGER PRIMARY KEY,
                            short_name VARCHAR(10),
                            full_name VARCHAR(255),
                            full_name_en VARCHAR(255)
                        );
                    """)
                except OperationalError:
                    cursor.execute("""
                        CREATE TEMP TABLE temp_core_language (
                            id INTEGER PRIMARY KEY,
                            short_name VARCHAR(10),
                            full_name VARCHAR(255),
                            full_name_en VARCHAR(255)
                        );
                    """)

                # Load fixture data into the temporary table
                self.stdout.write('Loading data into temporary table')
                for record in json_data:
                    pk = record["pk"]
                    fields = record["fields"]
                    short_name = fields["short_name"]
                    full_name = fields["full_name"]
                    full_name_en = fields["full_name_en"]

                    cursor.execute("""
                        INSERT INTO temp_core_language (id, short_name, full_name, full_name_en)
                        VALUES (%s, %s, %s, %s)
                        ON CONFLICT (id) DO UPDATE
                        SET short_name = EXCLUDED.short_name,
                            full_name = EXCLUDED.full_name,
                            full_name_en = EXCLUDED.full_name_en;
                    """, [pk, short_name, full_name, full_name_en])

                # Correct IDs and update references
                self.stdout.write('Updating core_language table and correcting references')
                cursor.execute("""
                    SELECT id, short_name, full_name, full_name_en FROM temp_core_language;
                """)

                for row in cursor.fetchall():
                    temp_id, temp_short_name, temp_full_name, temp_full_name_en = row

                    try:
                        language = Language.objects.get(short_name=temp_short_name)
                        if language.id != temp_id:
                            # Update references if ID has changed
                            language.id = temp_id
                        language.short_name = temp_short_name
                        language.full_name = temp_full_name
                        language.full_name_en = temp_full_name_en
                        language.save()
                    except Language.DoesNotExist:
                        Language.objects.create(
                            id=temp_id,
                            short_name=temp_short_name,
                            full_name=temp_full_name,
                            full_name_en=temp_full_name_en
                        )

                self.stdout.write('Successfully synchronized core_language table')

        except Exception as e:
            self.stdout.write(self.style.ERROR(f'Error: {str(e)}'))
