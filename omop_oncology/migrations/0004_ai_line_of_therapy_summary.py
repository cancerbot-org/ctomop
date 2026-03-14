from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('omop_oncology', '0003_remove_infectionstatus_infection_concept_and_more'),
    ]

    operations = [
        migrations.CreateModel(
            name='AILineOfTherapySummary',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('ai_lines_of_therapy_summary_id', models.CharField(blank=True, db_index=True, help_text='Source document ID from ai_lines_of_therapy_summary Firestore collection', max_length=255, null=True)),
                ('outcome', models.TextField(blank=True, help_text='Line outcome (e.g. PR, PD, CR, SD)', null=True)),
                ('active_ingredients', models.TextField(blank=True, help_text='All active ingredients, comma-separated (resolved from medicationMappings)', null=True)),
                ('active_ingredients_induction', models.TextField(blank=True, help_text='Induction-phase ingredients, comma-separated', null=True)),
                ('active_ingredients_maintenance', models.TextField(blank=True, help_text='Maintenance-phase ingredients, comma-separated', null=True)),
                ('has_bispecifics', models.BooleanField(default=False, help_text='True if the regimen contains a bispecific antibody')),
                ('has_transplant', models.BooleanField(default=False, help_text='True if a stem-cell transplant procedure is in the line')),
                ('has_cart', models.BooleanField(default=False, help_text='True if a CAR-T therapy (procedure or medication) is in the line')),
                ('procedures', models.TextField(blank=True, help_text='Procedure names, comma-separated (resolved from procedureMappings)', null=True)),
                ('is_clinical_trial', models.BooleanField(default=False)),
                ('clinical_trial_identifier', models.CharField(blank=True, max_length=255, null=True)),
                ('censoring_date', models.DateField(blank=True, null=True)),
                ('is_validated', models.BooleanField(default=False, help_text='Manually validated by a clinician or data-ops reviewer')),
                ('prompt_version', models.CharField(blank=True, help_text='Version of the AI prompt used to extract this LOT', max_length=50, null=True)),
                ('notes', models.TextField(blank=True, null=True)),
                ('source_created_at', models.DateTimeField(blank=True, help_text='created_at from the upstream Firestore document', null=True)),
                ('source_updated_at', models.DateTimeField(blank=True, help_text='updated_at from the upstream Firestore document', null=True)),
                ('created_at', models.DateTimeField(auto_now_add=True)),
                ('updated_at', models.DateTimeField(auto_now=True)),
                ('episode', models.OneToOneField(
                    help_text='The OMOP Episode representing this line of therapy',
                    on_delete=django.db.models.deletion.CASCADE,
                    related_name='ai_summary',
                    to='omop_oncology.episode',
                )),
            ],
            options={
                'db_table': 'ai_line_of_therapy_summary',
                'indexes': [
                    models.Index(fields=['episode'], name='ai_lot_episode_idx'),
                    models.Index(fields=['ai_lines_of_therapy_summary_id'], name='ai_lot_source_id_idx'),
                ],
            },
        ),
    ]
