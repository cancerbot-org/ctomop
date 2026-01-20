import React, { useState, useEffect } from 'react';
import { PatientInfo } from '../../types/patient';
import { Input } from '../UI/Input';
import { Select } from '../UI/Select';
import { FormField } from '../UI/FormField';

interface FollicularLymphomaTabProps {
  patientInfo: PatientInfo;
  onSave: (data: Partial<PatientInfo>) => Promise<void>;
}

export const FollicularLymphomaTab: React.FC<FollicularLymphomaTabProps> = ({ patientInfo, onSave }) => {
  const [formData, setFormData] = useState<Partial<PatientInfo>>(patientInfo);
  const [saving, setSaving] = useState(false);

  useEffect(() => {
    setFormData(patientInfo);
  }, [patientInfo]);

  const handleChange = (field: string, value: any) => {
    setFormData((prev: any) => ({ ...prev, [field]: value }));
  };

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    setSaving(true);
    try {
      await onSave(formData);
      alert('Information saved successfully!');
    } catch (error) {
      alert('Error saving information');
    } finally {
      setSaving(false);
    }
  };

  const gelfOptions = [
    { value: 'Met', label: 'GELF Criteria Met' },
    { value: 'Not Met', label: 'GELF Criteria Not Met' },
    { value: 'Unknown', label: 'Unknown' },
  ];

  const flipiOptions = [
    { value: 0, label: '0 - Low Risk' },
    { value: 1, label: '1 - Low Risk' },
    { value: 2, label: '2 - Intermediate Risk' },
    { value: 3, label: '3 - Intermediate Risk' },
    { value: 4, label: '4 - High Risk' },
    { value: 5, label: '5 - High Risk' },
  ];

  const gradeOptions = [
    { value: 'Grade 1', label: 'Grade 1 (0-5 centroblasts/HPF)' },
    { value: 'Grade 2', label: 'Grade 2 (6-15 centroblasts/HPF)' },
    { value: 'Grade 3a', label: 'Grade 3a (>15 centroblasts/HPF, centrocytes present)' },
    { value: 'Grade 3b', label: 'Grade 3b (solid sheets of centroblasts)' },
  ];

  return (
    <form onSubmit={handleSubmit} className="space-y-6">
      <div className="bg-white rounded-lg shadow-sm p-8">
        <div className="space-y-4">
          {/* GELF Criteria and FLIPI Score */}
          <div className="grid grid-cols-2 gap-4">
            <FormField label="GELF Criteria">
              <Select
                value={formData.gelf_criteria || ''}
                onChange={(e) => handleChange('gelf_criteria', e.target.value)}
                options={gelfOptions}
              />
            </FormField>

            <FormField label="FLIPI Score">
              <Select
                value={formData.flipi_score || ''}
                onChange={(e) => handleChange('flipi_score', parseInt(e.target.value))}
                options={flipiOptions}
              />
            </FormField>
          </div>

          {/* Tumor Grade */}
          <div className="grid grid-cols-2 gap-4">
            <FormField label="Tumor Grade">
              <Select
                value={formData.tumor_grade || ''}
                onChange={(e) => handleChange('tumor_grade', e.target.value)}
                options={gradeOptions}
              />
            </FormField>

            <div></div>
          </div>
        </div>

        <div className="mt-8">
          <button
            type="submit"
            disabled={saving}
            className="px-6 py-2 bg-blue-600 text-white rounded-md hover:bg-blue-700 disabled:bg-gray-400"
          >
            {saving ? 'Saving...' : 'Save Changes'}
          </button>
        </div>
      </div>
    </form>
  );
};