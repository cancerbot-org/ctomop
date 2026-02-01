# Migration to make ConditionOccurrence fields nullable

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('omop_core', '0030_add_patientinfo_fields'),
    ]

    operations = [
        # Make ConditionOccurrence fields nullable using raw SQL
        # Only alter columns that exist
        migrations.RunSQL(
            sql="""
                DO $$
                BEGIN
                    -- Basic fields
                    IF EXISTS (SELECT 1 FROM information_schema.columns 
                              WHERE table_name='condition_occurrence' AND column_name='condition_status_source_value') THEN
                        ALTER TABLE condition_occurrence ALTER COLUMN condition_status_source_value DROP NOT NULL;
                    END IF;
                    
                    IF EXISTS (SELECT 1 FROM information_schema.columns 
                              WHERE table_name='condition_occurrence' AND column_name='condition_source_value') THEN
                        ALTER TABLE condition_occurrence ALTER COLUMN condition_source_value DROP NOT NULL;
                    END IF;
                    
                    IF EXISTS (SELECT 1 FROM information_schema.columns 
                              WHERE table_name='condition_occurrence' AND column_name='stop_reason') THEN
                        ALTER TABLE condition_occurrence ALTER COLUMN stop_reason DROP NOT NULL;
                    END IF;
                    
                    -- Cancer fields
                    IF EXISTS (SELECT 1 FROM information_schema.columns 
                              WHERE table_name='condition_occurrence' AND column_name='ajcc_clinical_m') THEN
                        ALTER TABLE condition_occurrence ALTER COLUMN ajcc_clinical_m DROP NOT NULL;
                    END IF;
                    
                    IF EXISTS (SELECT 1 FROM information_schema.columns 
                              WHERE table_name='condition_occurrence' AND column_name='ajcc_clinical_n') THEN
                        ALTER TABLE condition_occurrence ALTER COLUMN ajcc_clinical_n DROP NOT NULL;
                    END IF;
                    
                    IF EXISTS (SELECT 1 FROM information_schema.columns 
                              WHERE table_name='condition_occurrence' AND column_name='ajcc_clinical_stage') THEN
                        ALTER TABLE condition_occurrence ALTER COLUMN ajcc_clinical_stage DROP NOT NULL;
                    END IF;
                    
                    IF EXISTS (SELECT 1 FROM information_schema.columns 
                              WHERE table_name='condition_occurrence' AND column_name='ajcc_clinical_t') THEN
                        ALTER TABLE condition_occurrence ALTER COLUMN ajcc_clinical_t DROP NOT NULL;
                    END IF;
                    
                    IF EXISTS (SELECT 1 FROM information_schema.columns 
                              WHERE table_name='condition_occurrence' AND column_name='ajcc_pathologic_m') THEN
                        ALTER TABLE condition_occurrence ALTER COLUMN ajcc_pathologic_m DROP NOT NULL;
                    END IF;
                    
                    IF EXISTS (SELECT 1 FROM information_schema.columns 
                              WHERE table_name='condition_occurrence' AND column_name='ajcc_pathologic_n') THEN
                        ALTER TABLE condition_occurrence ALTER COLUMN ajcc_pathologic_n DROP NOT NULL;
                    END IF;
                    
                    IF EXISTS (SELECT 1 FROM information_schema.columns 
                              WHERE table_name='condition_occurrence' AND column_name='ajcc_pathologic_stage') THEN
                        ALTER TABLE condition_occurrence ALTER COLUMN ajcc_pathologic_stage DROP NOT NULL;
                    END IF;
                    
                    IF EXISTS (SELECT 1 FROM information_schema.columns 
                              WHERE table_name='condition_occurrence' AND column_name='ajcc_pathologic_t') THEN
                        ALTER TABLE condition_occurrence ALTER COLUMN ajcc_pathologic_t DROP NOT NULL;
                    END IF;
                    
                    IF EXISTS (SELECT 1 FROM information_schema.columns 
                              WHERE table_name='condition_occurrence' AND column_name='estrogen_receptor_status') THEN
                        ALTER TABLE condition_occurrence ALTER COLUMN estrogen_receptor_status DROP NOT NULL;
                    END IF;
                    
                    IF EXISTS (SELECT 1 FROM information_schema.columns 
                              WHERE table_name='condition_occurrence' AND column_name='her2_status') THEN
                        ALTER TABLE condition_occurrence ALTER COLUMN her2_status DROP NOT NULL;
                    END IF;
                    
                    IF EXISTS (SELECT 1 FROM information_schema.columns 
                              WHERE table_name='condition_occurrence' AND column_name='histologic_grade') THEN
                        ALTER TABLE condition_occurrence ALTER COLUMN histologic_grade DROP NOT NULL;
                    END IF;
                    
                    IF EXISTS (SELECT 1 FROM information_schema.columns 
                              WHERE table_name='condition_occurrence' AND column_name='nuclear_grade') THEN
                        ALTER TABLE condition_occurrence ALTER COLUMN nuclear_grade DROP NOT NULL;
                    END IF;
                    
                    IF EXISTS (SELECT 1 FROM information_schema.columns 
                              WHERE table_name='condition_occurrence' AND column_name='progesterone_receptor_status') THEN
                        ALTER TABLE condition_occurrence ALTER COLUMN progesterone_receptor_status DROP NOT NULL;
                    END IF;
                    
                    IF EXISTS (SELECT 1 FROM information_schema.columns 
                              WHERE table_name='condition_occurrence' AND column_name='staging_system') THEN
                        ALTER TABLE condition_occurrence ALTER COLUMN staging_system DROP NOT NULL;
                    END IF;
                    
                    IF EXISTS (SELECT 1 FROM information_schema.columns 
                              WHERE table_name='condition_occurrence' AND column_name='staging_system_version') THEN
                        ALTER TABLE condition_occurrence ALTER COLUMN staging_system_version DROP NOT NULL;
                    END IF;
                    
                    IF EXISTS (SELECT 1 FROM information_schema.columns 
                              WHERE table_name='condition_occurrence' AND column_name='tumor_laterality') THEN
                        ALTER TABLE condition_occurrence ALTER COLUMN tumor_laterality DROP NOT NULL;
                    END IF;
                END $$;
            """,
            reverse_sql=migrations.RunSQL.noop
        ),
    ]
