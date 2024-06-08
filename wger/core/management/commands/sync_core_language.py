import json
import os
from django.core.management.base import BaseCommand
from django.db import connection, transaction

class Command(BaseCommand):
    help = 'Synchronize core_language table with fixture data from languages.json'

    def handle(self, *args, **kwargs):
        try:
            # Define the path to the languages.json file
            json_file_path = os.path.join('wger', 'core', 'fixtures', 'languages.json')
            self.stdout.write(self.style.NOTICE(f'JSON file path: {json_file_path}'))
    
            # Check if the file exists
            if not os.path.exists(json_file_path):
                self.stdout.write(self.style.ERROR(f'File not found: {json_file_path}'))
                return
    
            # Load JSON data from languages.json
            self.stdout.write(self.style.NOTICE('Loading data from languages.json'))
            with open(json_file_path, 'r', encoding='utf-8') as file:
                json_data = json.load(file)
            
            self.stdout.write(self.style.NOTICE(f'Successfully loaded JSON data. Records count: {len(json_data)}'))
    
            with transaction.atomic():
                with connection.cursor() as cursor:
                    # Disable foreign key constraints
                    self.stdout.write(self.style.NOTICE('Disabling foreign key constraints'))
                    cursor.execute("SET session_replication_role = 'replica';")
                    
                    # Create a temporary table
                    self.stdout.write(self.style.NOTICE('Creating temporary table'))
                    cursor.execute("""
                        CREATE TEMP TABLE temp_core_language (
                            id INT PRIMARY KEY,
                            short_name VARCHAR(10),
                            full_name VARCHAR(255),
                            full_name_en VARCHAR(255)
                        );
                    """)
                    
                    # Load fixture data into the temporary table
                    self.stdout.write(self.style.NOTICE('Loading data into temporary table'))
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
                    self.stdout.write(self.style.NOTICE('Updating core_language table and correcting references'))
                    cursor.execute("""
                        DO $$ 
                        DECLARE 
                            rec RECORD;
                        BEGIN
                            FOR rec IN (SELECT * FROM temp_core_language) LOOP
                                -- Update references if ID has changed
                                IF EXISTS (SELECT 1 FROM core_language WHERE short_name = rec.short_name AND id <> rec.id) THEN
                                    -- Inside the loop for updating core_language table and correcting references
                                    UPDATE exercises_exercise SET language_id = rec.id WHERE language_id = (SELECT id FROM core_language WHERE short_name = rec.short_name);
                                    UPDATE exercises_historicalexercise SET language_id = rec.id WHERE language_id = (SELECT id FROM core_language WHERE short_name = rec.short_name);
                                    UPDATE nutrition_ingredient SET language_id = rec.id WHERE language_id = (SELECT id FROM core_language WHERE short_name = rec.short_name);
                                    UPDATE nutrition_weightunit SET language_id = rec.id WHERE language_id = (SELECT id FROM core_language WHERE short_name = rec.short_name);
                                    -- Add more tables as needed
                                    UPDATE core_language
                                    SET id = rec.id,
                                        short_name = rec.short_name,
                                        full_name = rec.full_name,
                                        full_name_en = rec.full_name_en
                                    WHERE short_name = rec.short_name;
                                ELSE
                                    INSERT INTO core_language (id, short_name, full_name, full_name_en)
                                    VALUES (rec.id, rec.short_name, rec.full_name, rec.full_name_en)
                                    ON CONFLICT (id) DO UPDATE
                                    SET short_name = EXCLUDED.short_name,
                                        full_name = EXCLUDED.full_name,
                                        full_name_en = EXCLUDED.full_name_en;
                                END IF;
                            END LOOP;
                        END $$;
                    """)
                    
                    # Re-enable foreign key constraints
                    self.stdout.write(self.style.NOTICE('Re-enabling foreign key constraints'))
                    cursor.execute("SET session_replication_role = 'origin';")
                    
                    self.stdout.write(self.style.SUCCESS('Successfully synchronized core_language table'))

        except Exception as e:
            self.stdout.write(self.style.ERROR(f'Error: {str(e)}'))
