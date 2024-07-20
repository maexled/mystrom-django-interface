# Generated by Django 5.0.7 on 2024-07-20 16:10

from django.db import migrations


def forwards(apps, schema_editor):
    # Create a new temporary table with the desired schema
    with schema_editor.connection.cursor() as cursor:
        cursor.execute("""
            CREATE TABLE shelly3em_results_temp (
                date TIMESTAMPTZ NOT NULL,
                device_id INTEGER NOT NULL,
                total_power FLOAT,
                PRIMARY KEY (date, device_id)
            )
        """)

        # Copy data from the old table to the new table
        cursor.execute("""
            INSERT INTO shelly3em_results_temp (date, device_id, total_power)
            SELECT date, device_id, total_power
            FROM shelly3em_results
        """)

        cursor.execute("""
            CREATE TABLE shelly3em_emeter_results_temp (
                date TIMESTAMPTZ NOT NULL,
                device_id INTEGER NOT NULL,
                emeter_id INTEGER NOT NULL,
                power FLOAT,
                pf FLOAT,
                current FLOAT,
                voltage FLOAT,
                total FLOAT,
                total_returned FLOAT,
                PRIMARY KEY (date, device_id, emeter_id)
            )
        """)

        cursor.execute("""
            INSERT INTO shelly3em_emeter_results_temp (date, device_id, emeter_id, power, pf, current, voltage, total, total_returned)
            SELECT 
                        (SELECT date FROM shelly3em_results WHERE id = old.result_id), 
                        (SELECT device_id FROM shelly3em_results WHERE id = old.result_id),
                        old.emeter_id, old.power, old.pf, old.current, old.voltage, old.total, old.total_returned
            FROM shelly3em_emeter_results old
        """)

        # Drop the old table
        cursor.execute("""
            DROP TABLE shelly3em_emeter_results
        """)

        cursor.execute("""
            DROP TABLE shelly3em_results
        """)

        # Rename the new table to the original table name
        cursor.execute("""
            ALTER TABLE shelly3em_results_temp
            RENAME TO shelly3em_results
        """)

        cursor.execute("""
            ALTER TABLE shelly3em_emeter_results_temp
            RENAME TO shelly3em_emeter_results
        """)

        # Create hypertable
        cursor.execute("""
            SELECT create_hypertable('shelly3em_results', 'date', migrate_data => true)
        """)
        cursor.execute("""
            SELECT create_hypertable('shelly3em_emeter_results', 'date', migrate_data => true)
        """)

def backwards(apps, schema_editor):
    pass

class Migration(migrations.Migration):

    dependencies = [
        ('shelly3em_rest', '0002_alter_shelly3ememeterresult_result'),
    ]

    operations = [
        migrations.RunPython(forwards, backwards)
    ]
