import React, { useState, useEffect } from 'react';
import { PatientInfo, User } from '../../types/patient';
import { Input } from '../UI/Input';
import { Select } from '../UI/Select';
import { FormField } from '../UI/FormField';

interface GeneralTabProps {
  patientInfo: PatientInfo;
  user: User;
  onSave: (data: Partial<PatientInfo> & { first_name?: string; last_name?: string }) => Promise<void>;
  onDiseaseChange?: (disease: string) => void; // Add callback for immediate disease change
}

export const GeneralTab: React.FC<GeneralTabProps> = ({ patientInfo, user, onSave, onDiseaseChange }) => {
  const [formData, setFormData] = useState<Partial<PatientInfo> & { first_name?: string; last_name?: string }>({
    first_name: user.first_name || '',
    last_name: user.last_name || '',
    ...patientInfo,
  });
  const [saving, setSaving] = useState(false);

  useEffect(() => {
    setFormData({
      first_name: user.first_name || '',
      last_name: user.last_name || '',
      ...patientInfo,
    });
  }, [patientInfo, user]);

  const handleChange = (field: string, value: any) => {
    setFormData((prev: any) => ({ ...prev, [field]: value }));
    
    // If disease changes, immediately update and notify parent
    if (field === 'disease' && onDiseaseChange) {
      onDiseaseChange(value);
      // Auto-save disease change
      onSave({ ...formData, [field]: value }).catch(err => {
        console.error('Error auto-saving disease:', err);
      });
    }
  };

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    setSaving(true);
    try {
      await onSave(formData);
      alert('Information saved successfully!');
    } catch (error) {
      console.error('Save error:', error);
      alert('Error saving information. Please check the console for details.');
    } finally {
      setSaving(false);
    }
  };

  const ethnicityOptions = [
    { value: 'Caucasian/European', label: 'Caucasian/European' },
    { value: 'African/Black', label: 'African/Black' },
    { value: 'Asian', label: 'Asian' },
    { value: 'Native American', label: 'Native American' },
    { value: "Other/Won't Say", label: "Other/Won't Say" },
  ];

  const genderOptions = [
    { value: 'Male', label: 'Male' },
    { value: 'Female', label: 'Female' },
    { value: 'Other', label: 'Other' },
  ];

  const karnofskyOptions = [
    { value: 100, label: '100 - Normal, no complaints' },
    { value: 90, label: '90 - Normal activity, minor symptoms' },
    { value: 80, label: '80 - Normal activity with effort' },
    { value: 70, label: '70 - Cares for self, unable to work' },
    { value: 60, label: '60 - Requires occasional assistance' },
    { value: 50, label: '50 - Requires considerable assistance' },
    { value: 40, label: '40 - Disabled, special care needed' },
    { value: 30, label: '30 - Severely disabled' },
    { value: 20, label: '20 - Very sick, hospitalization needed' },
    { value: 10, label: '10 - Moribund' },
    { value: 0, label: '0 - Dead' },
  ];

  const ecogOptions = [
    { value: 0, label: '0 - Fully active' },
    { value: 1, label: '1 - Restricted in physically strenuous activity' },
    { value: 2, label: '2 - Ambulatory and capable of self-care' },
    { value: 3, label: '3 - Capable of only limited self-care' },
    { value: 4, label: '4 - Completely disabled' },
    { value: 5, label: '5 - Dead' },
  ];

  const yesNoOptions = [
    { value: 'Yes', label: 'Yes' },
    { value: 'No', label: 'No' },
  ];

  const neuropathyOptions = [
    { value: 0, label: 'None' },
    { value: 1, label: 'Grade 1 - Mild' },
    { value: 2, label: 'Grade 2 - Moderate' },
    { value: 3, label: 'Grade 3 - Severe' },
    { value: 4, label: 'Grade 4 - Life-threatening' },
  ];

  return (
    <form onSubmit={handleSubmit} className="space-y-6">
      <div className="bg-white rounded-lg shadow-sm p-8">
        <div className="space-y-4">
          {/* First Name and Last Name */}
          <div className="grid grid-cols-2 gap-4">
            <FormField label="First Name">
              <Input
                value={formData.first_name || ''}
                onChange={(e) => handleChange('first_name', e.target.value)}
              />
            </FormField>

            <FormField label="Last Name">
              <Input
                value={formData.last_name || ''}
                onChange={(e) => handleChange('last_name', e.target.value)}
              />
            </FormField>
          </div>

          {/* Age and Gender */}
          <div className="grid grid-cols-2 gap-4">
            <FormField label="Patient Age">
              <Input
                type="number"
                value={formData.patient_age || ''}
                onChange={(e) => handleChange('patient_age', parseInt(e.target.value))}
              />
            </FormField>

            <FormField label="Gender">
              <Select
                value={formData.gender || ''}
                onChange={(e) => handleChange('gender', e.target.value)}
                options={genderOptions}
              />
            </FormField>
          </div>

          {/* Weight and Height */}
          <div className="grid grid-cols-2 gap-4">
            <FormField label="Weight">
              <div className="flex gap-2">
                <Input
                  type="number"
                  step="0.1"
                  value={formData.weight_kg || ''}
                  onChange={(e) => handleChange('weight_kg', parseFloat(e.target.value))}
                  className="flex-1"
                />
                <Select
                  value="kg"
                  disabled
                  options={[{ value: 'kg', label: 'Kilograms' }]}
                  className="w-40"
                />
              </div>
            </FormField>

            <FormField label="Height">
              <div className="flex gap-2">
                <Input
                  type="number"
                  step="0.1"
                  value={formData.height_cm || ''}
                  onChange={(e) => handleChange('height_cm', parseFloat(e.target.value))}
                  className="flex-1"
                />
                <Select
                  value="cm"
                  disabled
                  options={[{ value: 'cm', label: 'Centimeters' }]}
                  className="w-40"
                />
              </div>
            </FormField>
          </div>

          {/* Ethnicity and Blood Pressure */}
          <div className="grid grid-cols-2 gap-4">
            <FormField label="Ethnicity">
              <Select
                value={formData.ethnicity || ''}
                onChange={(e) => handleChange('ethnicity', e.target.value)}
                options={ethnicityOptions}
              />
            </FormField>

            <FormField label="Blood Pressure (SBP / DBP)">
              <div className="flex gap-2 items-center">
                <Input
                  type="number"
                  placeholder="SBP"
                  value={formData.systolic_bp || ''}
                  onChange={(e) => handleChange('systolic_bp', parseInt(e.target.value))}
                  className="flex-1"
                />
                <span className="text-gray-500">/</span>
                <Input
                  type="number"
                  placeholder="DBP"
                  value={formData.diastolic_bp || ''}
                  onChange={(e) => handleChange('diastolic_bp', parseInt(e.target.value))}
                  className="flex-1"
                />
              </div>
            </FormField>
          </div>

          {/* Location and Zip/Postal Code */}
          <div className="grid grid-cols-2 gap-4">
            <FormField label="Location">
              <Select
                value={formData.location || ''}
                onChange={(e) => handleChange('location', e.target.value)}
                options={[
                  { value: 'United Kingdom', label: 'United Kingdom' },
                  { value: 'United States', label: 'United States' },
                  { value: 'Canada', label: 'Canada' },
                  { value: 'Other', label: 'Other' },
                ]}
              />
            </FormField>

            <FormField label="Zip/Postal Code">
              <Input
                placeholder="Zip/Postal Code"
                value={formData.postal_code || ''}
                onChange={(e) => handleChange('postal_code', e.target.value)}
              />
            </FormField>
          </div>

          {/* Disease and Stage */}
          <div className="grid grid-cols-2 gap-4">
            <FormField label="Disease">
              <Select
                value={formData.disease || ''}
                onChange={(e) => handleChange('disease', e.target.value)}
                options={[
                  { value: 'Multiple Myeloma', label: 'Multiple Myeloma' },
                  { value: 'Follicular Lymphoma', label: 'Follicular Lymphoma' },
                  { value: 'Breast Cancer', label: 'Breast Cancer' },
                  { value: 'Lung Cancer', label: 'Lung Cancer' },
                  { value: 'Colorectal Cancer', label: 'Colorectal Cancer' },
                  { value: 'Other', label: 'Other' },
                ]}
              />
            </FormField>

            <FormField label="Stage">
              <Select
                value={formData.stage || ''}
                onChange={(e) => handleChange('stage', e.target.value)}
                options={[
                  { value: 'Unknown', label: 'Unknown' },
                  { value: 'Stage I', label: 'Stage I' },
                  { value: 'Stage II', label: 'Stage II' },
                  { value: 'Stage III', label: 'Stage III' },
                  { value: 'Stage IV', label: 'Stage IV' },
                ]}
              />
            </FormField>
          </div>

          {/* Karnofsky and ECOG */}
          <div className="grid grid-cols-2 gap-4">
            <FormField label="Karnofsky Performance Score">
              <Select
                value={formData.karnofsky_performance_status || ''}
                onChange={(e) => handleChange('karnofsky_performance_status', parseInt(e.target.value))}
                options={karnofskyOptions}
              />
            </FormField>

            <FormField label="ECOG Performance Status">
              <Select
                value={formData.ecog_performance_status || ''}
                onChange={(e) => handleChange('ecog_performance_status', parseInt(e.target.value))}
                options={ecogOptions}
              />
            </FormField>
          </div>

          {/* Active Malignancies and Active Infection */}
          <div className="grid grid-cols-2 gap-4">
            <FormField label="No Other Active Malignancies">
              <Select
                value={formData.active_malignancies || 'Yes'}
                onChange={(e) => handleChange('active_malignancies', e.target.value)}
                options={yesNoOptions}
              />
            </FormField>

            <FormField label="No Active Infection">
              <Select
                value={formData.active_infection ? 'No' : 'Yes'}
                onChange={(e) => handleChange('active_infection', e.target.value === 'No')}
                options={yesNoOptions}
              />
            </FormField>
          </div>

          {/* Preexisting Conditions and Peripheral Neuropathy */}
          <div className="grid grid-cols-2 gap-4">
            <FormField label="Preexisting Conditions">
              <Select
                value={formData.preexisting_conditions || ''}
                onChange={(e) => handleChange('preexisting_conditions', e.target.value)}
                options={[
                  { value: 'None', label: 'Preexisting Conditions' },
                  { value: 'Diabetes', label: 'Diabetes' },
                  { value: 'Hypertension', label: 'Hypertension' },
                  { value: 'Cardiac Issues', label: 'Cardiac Issues' },
                  { value: 'Other', label: 'Other' },
                ]}
              />
            </FormField>

            <FormField label="Peripheral Neuropathy Grade">
              <Select
                value={formData.peripheral_neuropathy_grade || ''}
                onChange={(e) => handleChange('peripheral_neuropathy_grade', parseInt(e.target.value))}
                options={neuropathyOptions}
              />
            </FormField>
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

