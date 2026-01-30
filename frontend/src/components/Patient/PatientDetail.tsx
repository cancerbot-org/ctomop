import React, { useState, useEffect } from 'react';
import {
  Box,
  Paper,
  Typography,
  CircularProgress,
  Alert,
  Tabs,
  Tab,
  Grid,
  Button,
  Divider,
  TextField,
  Select,
  MenuItem,
  FormControl,
  InputLabel,
} from '@mui/material';
import { useParams, useNavigate } from 'react-router-dom';
import { ArrowLeft, Save } from 'lucide-react';
import api from '../../api/axios';

interface TabPanelProps {
  children?: React.ReactNode;
  index: number;
  value: number;
}

function TabPanel(props: TabPanelProps) {
  const { children, value, index, ...other } = props;
  return (
    <div
      role="tabpanel"
      hidden={value !== index}
      id={`patient-tabpanel-${index}`}
      aria-labelledby={`patient-tab-${index}`}
      {...other}
    >
      {value === index && <Box sx={{ p: 3 }}>{children}</Box>}
    </div>
  );
}

// Dropdown options
const GENDER_OPTIONS = ['Male', 'Female', 'Other', 'Unknown'];
const COUNTRY_OPTIONS = ['United States', 'Canada', 'United Kingdom', 'Germany', 'France', 'Spain', 'Italy', 'Other'];
const US_STATES = [
  'AL', 'AK', 'AZ', 'AR', 'CA', 'CO', 'CT', 'DE', 'FL', 'GA', 'HI', 'ID', 'IL', 'IN', 'IA', 'KS',
  'KY', 'LA', 'ME', 'MD', 'MA', 'MI', 'MN', 'MS', 'MO', 'MT', 'NE', 'NV', 'NH', 'NJ', 'NM', 'NY',
  'NC', 'ND', 'OH', 'OK', 'OR', 'PA', 'RI', 'SC', 'SD', 'TN', 'TX', 'UT', 'VT', 'VA', 'WA', 'WV',
  'WI', 'WY', 'DC', 'PR', 'GU', 'VI'
];
const ETHNICITY_OPTIONS = ['Caucasian/White', 'Hispanic/Latino', 'Black/African-American', 'Asian', 'Native American'];
const DISEASE_OPTIONS = ['Breast Cancer', 'Follicular Lymphoma', 'Multiple Myeloma', 'Lung Cancer', 'Colon Cancer', 'Other'];
const STAGE_OPTIONS = ['0', 'I', 'IA', 'IB', 'II', 'IIA', 'IIB', 'III', 'IIIA', 'IIIB', 'IIIC', 'IV', 'Unknown'];
const ECOG_OPTIONS = ['0', '1', '2', '3', '4', '5'];
const KARNOFSKY_OPTIONS = ['100', '90', '80', '70', '60', '50', '40', '30', '20', '10', '0'];
const YES_NO_OPTIONS = ['Yes', 'No', 'Unknown'];
const POSITIVE_NEGATIVE_OPTIONS = ['Positive', 'Negative', 'Unknown'];
const ER_PR_OPTIONS = ['Positive', 'Negative', 'Borderline', 'Unknown'];
const HER2_OPTIONS = ['Positive', 'Negative', 'Equivocal', 'Unknown'];
const FLIPI_RISK_OPTIONS = ['Low', 'Intermediate', 'High'];
const ISS_STAGE_OPTIONS = ['Stage I', 'Stage II', 'Stage III'];
const CYTOGENETIC_RISK_OPTIONS = ['Standard Risk', 'High Risk', 'Very High Risk'];
const THERAPY_OUTCOME_OPTIONS = ['Complete Response', 'Partial Response', 'Stable Disease', 'Progressive Disease', 'Unknown'];
const SMOKING_STATUS_OPTIONS = ['Never Smoker', 'Former Smoker', 'Current Smoker', 'Unknown'];
const ALCOHOL_USE_OPTIONS = ['None', 'Occasional', 'Moderate', 'Heavy', 'Unknown'];
const EXERCISE_FREQUENCY_OPTIONS = ['None', 'Rarely', '1-2 times/week', '3-4 times/week', '5+ times/week', 'Daily', 'Unknown'];
const REFRACTORY_STATUS_OPTIONS = ['Responsive', 'Stable', 'Refractory', 'Unknown'];
const DIET_TYPE_OPTIONS = ['Regular', 'Vegetarian', 'Vegan', 'Mediterranean', 'Low-carb', 'Ketogenic', 'Other'];
const SLEEP_QUALITY_OPTIONS = ['Excellent', 'Good', 'Fair', 'Poor', 'Very Poor'];
const STRESS_LEVEL_OPTIONS = ['None', 'Low', 'Moderate', 'High', 'Very High'];
const SOCIAL_SUPPORT_OPTIONS = ['Excellent', 'Good', 'Fair', 'Poor', 'None'];
const EMPLOYMENT_STATUS_OPTIONS = ['Employed Full-time', 'Employed Part-time', 'Self-employed', 'Unemployed', 'Retired', 'Disabled', 'Student', 'Homemaker'];
const EDUCATION_LEVEL_OPTIONS = ['Less than High School', 'High School Graduate', 'Some College', 'Associate Degree', 'Bachelor Degree', 'Master Degree', 'Doctoral Degree', 'Professional Degree'];
const MARITAL_STATUS_OPTIONS = ['Single', 'Married', 'Divorced', 'Widowed', 'Separated', 'Domestic Partnership'];
const INSURANCE_TYPE_OPTIONS = ['Private Insurance', 'Medicare', 'Medicaid', 'Veterans Affairs', 'Other Government', 'Self-pay', 'None'];

// Genetic mutation options
const GENE_OPTIONS = ['BRCA1', 'BRCA2', 'TP53', 'PIK3CA', 'PTEN', 'ATM', 'CHEK2', 'PALB2', 'CDH1', 'ERBB2'];
const MUTATION_OPTIONS: { [key: string]: string[] } = {
  'BRCA1': ['c.68_69delAG', 'c.5266dupC', 'c.181T>G', 'c.3756_3759del', '185delAG'],
  'BRCA2': ['c.5946delT', 'c.9097dupA', 'c.7617+1G>A', '6174delT', 'c.8537_8538del'],
  'TP53': ['R175H', 'R248Q', 'R273H', 'R248W', 'R282W'],
  'PIK3CA': ['E542K', 'E545K', 'H1047R', 'H1047L', 'E726K'],
  'PTEN': ['R130*', 'R173C', 'R233*', 'R335*', 'c.209+1G>T'],
  'ATM': ['c.5932G>T', 'c.6095G>A', 'c.8122G>A', 'c.7271T>G'],
  'CHEK2': ['1100delC', 'I157T', 'R117G', 'IVS2+1G>A'],
  'PALB2': ['c.3113G>A', 'c.1676del', 'c.509_510delGA', 'c.172_175delTTGT'],
  'CDH1': ['c.1018A>G', 'c.1137G>A', 'c.283C>T', 'c.1901C>T'],
  'ERBB2': ['L755S', 'V777L', 'G776delinsVC', 'D769H']
};
const ORIGIN_OPTIONS = ['Germline', 'Somatic', 'Unknown'];
const INTERPRETATION_OPTIONS = ['Pathogenic', 'Likely pathogenic', 'VUS', 'Likely benign', 'Benign'];

// Disease-specific therapy options
const BREAST_CANCER_FIRST_LINE = [
  'AC-T',
  'AC-T (Doxorubicin/Cyclophosphamide followed by Paclitaxel)',
  'TC',
  'TC (Docetaxel/Cyclophosphamide)',
  'TAC (Docetaxel/Doxorubicin/Cyclophosphamide)',
  'Paclitaxel/Trastuzumab/Pertuzumab',
  'Paclitaxel/Trastuzumab/Pertuzumab (HER2+)',
  'Docetaxel/Trastuzumab/Pertuzumab',
  'TCH (Docetaxel/Carboplatin/Trastuzumab)',
  'Tamoxifen',
  'Letrozole',
  'Anastrozole',
  'Exemestane',
  'CDK4/6 Inhibitor + Letrozole',
  'CDK4/6 Inhibitor + Anastrozole',
  'CDK4/6 Inhibitor + Fulvestrant',
  'Palbociclib + Letrozole',
  'Ribociclib + Letrozole',
  'Abemaciclib + Letrozole',
  'Fulvestrant',
  'Hormone Therapy (Tamoxifen/Aromatase Inhibitor)',
  'FEC (5-FU/Epirubicin/Cyclophosphamide)',
  'CMF (Cyclophosphamide/Methotrexate/5-FU)',
  'Paclitaxel',
  'Docetaxel',
  'Capecitabine',
  'Doxorubicin',
  'Other'
];

const BREAST_CANCER_SECOND_LINE = [
  'Capecitabine',
  'T-DM1',
  'T-DM1 (Trastuzumab emtansine)',
  'T-DXd (Trastuzumab deruxtecan)',
  'Eribulin',
  'Gemcitabine/Carboplatin',
  'Paclitaxel/Bevacizumab',
  'Olaparib',
  'Talazoparib',
  'PARP Inhibitor (BRCA+)',
  'Sacituzumab govitecan',
  'Vinorelbine',
  'Ixabepilone',
  'Lapatinib + Capecitabine',
  'Neratinib + Capecitabine',
  'Fulvestrant',
  'Everolimus + Exemestane',
  'Alpelisib + Fulvestrant',
  'Tucatinib/Trastuzumab/Capecitabine',
  'Pertuzumab + Trastuzumab',
  'Other'
];

const BREAST_CANCER_LATER_LINE = [
  'T-DXd',
  'T-DXd (Trastuzumab deruxtecan)',
  'Sacituzumab govitecan',
  'Vinorelbine',
  'Eribulin',
  'Ixabepilone',
  'Pembrolizumab',
  'Atezolizumab + Nab-paclitaxel',
  'PARP Inhibitor',
  'Olaparib',
  'Talazoparib',
  'Margetuximab',
  'Lapatinib',
  'Neratinib',
  'Gemcitabine',
  'Carboplatin',
  'Cisplatin',
  'Methotrexate',
  'Mitomycin',
  'Clinical Trial',
  'Other'
];

const LYMPHOMA_FIRST_LINE = [
  'R-CHOP (Rituximab/Cyclophosphamide/Doxorubicin/Vincristine/Prednisone)',
  'BR (Bendamustine/Rituximab)',
  'R-CVP (Rituximab/Cyclophosphamide/Vincristine/Prednisone)',
  'Rituximab Monotherapy',
  'Watch and Wait',
  'Other'
];

const LYMPHOMA_SECOND_LINE = [
  'R-ICE (Rituximab/Ifosfamide/Carboplatin/Etoposide)',
  'R-DHAP (Rituximab/Dexamethasone/Cytarabine/Cisplatin)',
  'BR (Bendamustine/Rituximab)',
  'Lenalidomide/Rituximab',
  'Obinutuzumab-based therapy',
  'Other'
];

const LYMPHOMA_LATER_LINE = [
  'Tazemetostat',
  'Lenalidomide/Rituximab',
  'PI3K Inhibitor (Copanlisib/Duvelisib/Idelalisib)',
  'Obinutuzumab Monotherapy',
  'Clinical Trial',
  'Other'
];

const MYELOMA_FIRST_LINE = [
  'VRd (Bortezomib/Lenalidomide/Dexamethasone)',
  'CyBorD (Cyclophosphamide/Bortezomib/Dexamethasone)',
  'DRd (Daratumumab/Lenalidomide/Dexamethasone)',
  'RVd (Lenalidomide/Bortezomib/Dexamethasone)',
  'KRd (Carfilzomib/Lenalidomide/Dexamethasone)',
  'Other'
];

const MYELOMA_SECOND_LINE = [
  'DVd (Daratumumab/Bortezomib/Dexamethasone)',
  'KRd (Carfilzomib/Lenalidomide/Dexamethasone)',
  'DRd (Daratumumab/Lenalidomide/Dexamethasone)',
  'Elotuzumab/Lenalidomide/Dexamethasone',
  'Ixazomib/Lenalidomide/Dexamethasone',
  'Carfilzomib/Dexamethasone',
  'Other'
];

const MYELOMA_LATER_LINE = [
  'Isatuximab/Pomalidomide/Dexamethasone',
  'Daratumumab/Pomalidomide/Dexamethasone',
  'Selinexor/Bortezomib/Dexamethasone',
  'Belantamab mafodotin',
  'CAR-T (Idecabtagene vicleucel/Ciltacabtagene autoleucel)',
  'Clinical Trial',
  'Other'
];

const PatientDetail: React.FC = () => {
  const { personId } = useParams<{ personId: string }>();
  const navigate = useNavigate();
  const [loading, setLoading] = useState(true);
  const [saving, setSaving] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [successMessage, setSuccessMessage] = useState<string | null>(null);
  const [patientInfo, setPatientInfo] = useState<any>(null);
  const [editedInfo, setEditedInfo] = useState<any>({});
  const [patientName, setPatientName] = useState<string>('');
  const [editedName, setEditedName] = useState<string>('');
  const [activeTab, setActiveTab] = useState(0);

  useEffect(() => {
    const fetchPatientInfo = async () => {
      if (!personId) return;

      try {
        setLoading(true);
        const response = await api.get(`/patient-info/${personId}/`);
        const patientData = response.data.patient_info;
        
        // Convert ECOG from integer to string for dropdown
        if (patientData.ecog_performance_status !== null && patientData.ecog_performance_status !== undefined) {
          patientData.ecog_performance_status = String(patientData.ecog_performance_status);
        }
        
        // Auto-compute Triple Negative status if not already set
        if (patientData.estrogen_receptor_status && patientData.progesterone_receptor_status && patientData.her2_status) {
          const isTripleNegative = 
            patientData.estrogen_receptor_status === 'Negative' &&
            patientData.progesterone_receptor_status === 'Negative' &&
            patientData.her2_status === 'Negative';
          patientData.tnbc_status = isTripleNegative;
        }
        
        setPatientInfo(patientData);
        setEditedInfo(patientData);
        
        if (response.data.user) {
          const user = response.data.user;
          const fullName = `${user.first_name} ${user.last_name}`.trim();
          setPatientName(fullName || user.username || `Patient ${personId}`);
          setEditedName(fullName || user.username || `Patient ${personId}`);
        } else {
          setPatientName(`Patient ${personId}`);
          setEditedName(`Patient ${personId}`);
        }
        
        setError(null);
      } catch (err: any) {
        setError(err.response?.data?.error || 'Failed to fetch patient information');
      } finally {
        setLoading(false);
      }
    };

    fetchPatientInfo();
  }, [personId]);

  const handleTabChange = (event: React.SyntheticEvent, newValue: number) => {
    setActiveTab(newValue);
  };

  const handleFieldChange = (field: string, value: any) => {
    const updatedInfo = { ...editedInfo, [field]: value };
    
    // Auto-compute Triple Negative status based on ER, PR, and HER2 statuses
    if (field === 'estrogen_receptor_status' || field === 'progesterone_receptor_status' || field === 'her2_status') {
      const er = field === 'estrogen_receptor_status' ? value : updatedInfo.estrogen_receptor_status;
      const pr = field === 'progesterone_receptor_status' ? value : updatedInfo.progesterone_receptor_status;
      const her2 = field === 'her2_status' ? value : updatedInfo.her2_status;
      
      // Triple negative if all three are Negative
      if (er === 'Negative' && pr === 'Negative' && her2 === 'Negative') {
        updatedInfo.tnbc_status = true;
      } else if (er || pr || her2) {
        // Only set to false if at least one status is defined and not all are negative
        updatedInfo.tnbc_status = false;
      }
    }
    
    setEditedInfo(updatedInfo);
    setSuccessMessage(null);
  };

  const handleMutationAdd = () => {
    const mutations = editedInfo.genetic_mutations || [];
    mutations.push({
      gene: '',
      mutation: '',
      origin: '',
      interpretation: ''
    });
    handleFieldChange('genetic_mutations', mutations);
  };

  const handleMutationRemove = (index: number) => {
    const mutations = [...(editedInfo.genetic_mutations || [])];
    mutations.splice(index, 1);
    handleFieldChange('genetic_mutations', mutations);
  };

  const handleMutationChange = (index: number, field: string, value: string) => {
    const mutations = [...(editedInfo.genetic_mutations || [])];
    mutations[index] = { ...mutations[index], [field]: value };
    
    // Reset mutation when gene changes
    if (field === 'gene') {
      mutations[index].mutation = '';
    }
    
    handleFieldChange('genetic_mutations', mutations);
  };

  const handleZipcodeChange = async (zipcode: string) => {
    handleFieldChange('postal_code', zipcode);
    
    // Only lookup for 5-digit US zipcodes
    if (zipcode && zipcode.length === 5 && /^\d{5}$/.test(zipcode)) {
      try {
        const response = await fetch(`https://api.zippopotam.us/us/${zipcode}`);
        if (response.ok) {
          const data = await response.json();
          if (data.places && data.places.length > 0) {
            const place = data.places[0];
            // Auto-populate city and state
            setEditedInfo({
              ...editedInfo,
              postal_code: zipcode,
              city: place['place name'],
              region: place['state']
            });
          }
        }
      } catch (error) {
        // Silently fail - user can still enter manually
        console.log('Zipcode lookup failed:', error);
      }
    }
  };

  const handleSave = async () => {
    try {
      setSaving(true);
      setError(null);
      
      // Save patient info
      await api.patch(`/patient-info/${personId}/`, editedInfo);
      
      // Update patient name if changed
      if (editedName !== patientName) {
        const nameParts = editedName.trim().split(' ');
        const firstName = nameParts[0] || '';
        const lastName = nameParts.slice(1).join(' ') || '';
        
        await api.patch(`/user/`, {
          first_name: firstName,
          last_name: lastName
        });
        
        setPatientName(editedName);
      }
      
      setPatientInfo(editedInfo);
      setSuccessMessage('Patient information saved successfully');
      
      setTimeout(() => setSuccessMessage(null), 3000);
    } catch (err: any) {
      setError(err.response?.data?.error || 'Failed to save patient information');
    } finally {
      setSaving(false);
    }
  };

  const calculateAge = (dateOfBirth: string) => {
    if (!dateOfBirth) return null;
    const today = new Date();
    const birthDate = new Date(dateOfBirth);
    let age = today.getFullYear() - birthDate.getFullYear();
    const monthDiff = today.getMonth() - birthDate.getMonth();
    if (monthDiff < 0 || (monthDiff === 0 && today.getDate() < birthDate.getDate())) {
      age--;
    }
    return age;
  };

  const formatDateForInput = (dateString: string) => {
    if (!dateString) return '';
    try {
      const date = new Date(dateString);
      return date.toISOString().split('T')[0];
    } catch {
      return '';
    }
  };

  const getDiseaseType = () => {
    const disease = editedInfo?.disease?.toLowerCase() || '';
    if (disease.includes('breast')) return 'breast';
    if (disease.includes('lymphoma')) return 'lymphoma';
    if (disease.includes('myeloma')) return 'myeloma';
    return 'other';
  };

  const getDiseaseTabLabel = () => {
    const diseaseType = getDiseaseType();
    switch (diseaseType) {
      case 'breast':
        return 'Breast Cancer';
      case 'lymphoma':
        return 'Follicular Lymphoma';
      case 'myeloma':
        return 'Multiple Myeloma';
      default:
        return 'Disease Specific';
    }
  };

  const getTherapyOptions = (line: 'first' | 'second' | 'later') => {
    const diseaseType = getDiseaseType();
    
    switch (diseaseType) {
      case 'breast':
        if (line === 'first') return BREAST_CANCER_FIRST_LINE;
        if (line === 'second') return BREAST_CANCER_SECOND_LINE;
        return BREAST_CANCER_LATER_LINE;
      case 'lymphoma':
        if (line === 'first') return LYMPHOMA_FIRST_LINE;
        if (line === 'second') return LYMPHOMA_SECOND_LINE;
        return LYMPHOMA_LATER_LINE;
      case 'myeloma':
        if (line === 'first') return MYELOMA_FIRST_LINE;
        if (line === 'second') return MYELOMA_SECOND_LINE;
        return MYELOMA_LATER_LINE;
      default:
        return ['Other'];
    }
  };

  if (loading) {
    return (
      <Box display="flex" justifyContent="center" alignItems="center" minHeight="400px">
        <CircularProgress />
      </Box>
    );
  }

  if (error && !patientInfo) {
    return (
      <Box p={3}>
        <Alert severity="error">{error}</Alert>
        <Button startIcon={<ArrowLeft />} onClick={() => navigate('/')} sx={{ mt: 2 }}>
          Back to Patient List
        </Button>
      </Box>
    );
  }

  const renderTextField = (label: string, field: string, fullWidth: boolean = false, type: string = 'text', disabled: boolean = false) => {
    return (
      <Grid item xs={12} md={fullWidth ? 12 : 6}>
        <TextField
          fullWidth
          label={label}
          type={type}
          value={editedInfo?.[field] || ''}
          onChange={(e) => handleFieldChange(field, e.target.value)}
          variant="outlined"
          size="small"
          disabled={disabled}
        />
      </Grid>
    );
  };

  const renderDateField = (label: string, field: string, fullWidth: boolean = false) => {
    return (
      <Grid item xs={12} md={fullWidth ? 12 : 6}>
        <TextField
          fullWidth
          label={label}
          type="date"
          value={formatDateForInput(editedInfo?.[field])}
          onChange={(e) => handleFieldChange(field, e.target.value)}
          variant="outlined"
          size="small"
          InputLabelProps={{ shrink: true }}
        />
      </Grid>
    );
  };

  const renderSelectField = (label: string, field: string, options: string[], fullWidth: boolean = false, disabled: boolean = false) => {
    const currentValue = editedInfo?.[field] || '';
    
    // Add current value to options if it exists but is not in the list
    const displayOptions = [...options];
    if (currentValue && !options.includes(currentValue)) {
      displayOptions.unshift(currentValue);
    }
    
    return (
      <Grid item xs={12} md={fullWidth ? 12 : 6}>
        <FormControl fullWidth size="small">
          <InputLabel>{label}</InputLabel>
          <Select
            value={currentValue}
            label={label}
            onChange={(e) => handleFieldChange(field, e.target.value)}
            disabled={disabled}
          >
            <MenuItem value="">
              <em>None</em>
            </MenuItem>
            {displayOptions.map((option) => (
              <MenuItem key={option} value={option}>
                {option}
              </MenuItem>
            ))}
          </Select>
        </FormControl>
      </Grid>
    );
  };

  const renderBreastCancerTab = () => (
    <Grid container spacing={3}>
      <Grid item xs={12}>
        <Typography variant="h6" gutterBottom>Tumor Characteristics</Typography>
      </Grid>
      {renderTextField('Histologic Type', 'histologic_type', true)}
      {renderSelectField('Stage', 'stage', STAGE_OPTIONS)}
      {renderTextField('Tumor Size (cm)', 'tumor_size', false, 'number')}
      {renderSelectField('Lymph Node Status', 'lymph_node_status', POSITIVE_NEGATIVE_OPTIONS)}
      {renderSelectField('Metastasis Status', 'metastasis_status', POSITIVE_NEGATIVE_OPTIONS)}
      
      <Grid item xs={12}>
        <Divider sx={{ my: 2 }} />
        <Typography variant="h6" gutterBottom sx={{ mt: 2 }}>
          Receptor Status
        </Typography>
      </Grid>
      {renderSelectField('Estrogen Receptor (ER) Status', 'estrogen_receptor_status', ER_PR_OPTIONS)}
      {renderSelectField('Progesterone Receptor (PR) Status', 'progesterone_receptor_status', ER_PR_OPTIONS)}
      {renderSelectField('HER2 Status', 'her2_status', HER2_OPTIONS)}
      
      <Grid item xs={12} sm={6}>
        <TextField
          fullWidth
          label="Triple Negative Status (Computed)"
          value={editedInfo.tnbc_status ? 'Yes' : 'No'}
          variant="outlined"
          disabled
          InputProps={{
            readOnly: true,
          }}
          helperText="Automatically computed from ER, PR, and HER2 status"
        />
      </Grid>
      
      <Grid item xs={12}>
        <Divider sx={{ my: 2 }} />
        <Typography variant="h6" gutterBottom sx={{ mt: 2 }}>
          Additional Biomarkers
        </Typography>
      </Grid>
      {renderTextField('Ki-67 Proliferation Index (%)', 'ki67_proliferation_index', false, 'number')}
      {renderTextField('PD-L1 Status (%)', 'pd_l1_tumor_cels', false, 'number')}
      
      <Grid item xs={12}>
        <Divider sx={{ my: 2 }} />
        <Typography variant="h6" gutterBottom sx={{ mt: 2 }}>
          Genetic Mutations
        </Typography>
      </Grid>
      
      <Grid item xs={12}>
        <Box sx={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', mb: 2 }}>
          <Typography variant="body2" color="text.secondary">
            {(editedInfo.genetic_mutations || []).length} mutation(s) identified
          </Typography>
          <Button
            variant="outlined"
            size="small"
            onClick={handleMutationAdd}
          >
            Add Mutation
          </Button>
        </Box>
        
        {(editedInfo.genetic_mutations || []).map((mutation: any, index: number) => (
          <Box key={index} sx={{ mb: 3, p: 2, border: '1px solid #e0e0e0', borderRadius: 1 }}>
            <Box sx={{ display: 'flex', justifyContent: 'space-between', mb: 2 }}>
              <Typography variant="subtitle2">Mutation {index + 1}</Typography>
              <Button
                size="small"
                color="error"
                onClick={() => handleMutationRemove(index)}
              >
                Remove
              </Button>
            </Box>
            <Grid container spacing={2}>
              <Grid item xs={12} sm={6} md={3}>
                <FormControl fullWidth size="small">
                  <InputLabel>Gene</InputLabel>
                  <Select
                    value={mutation.gene || ''}
                    label="Gene"
                    onChange={(e) => handleMutationChange(index, 'gene', e.target.value)}
                  >
                    {GENE_OPTIONS.map((gene) => (
                      <MenuItem key={gene} value={gene}>{gene}</MenuItem>
                    ))}
                  </Select>
                </FormControl>
              </Grid>
              <Grid item xs={12} sm={6} md={3}>
                <FormControl fullWidth size="small" disabled={!mutation.gene}>
                  <InputLabel>Mutation</InputLabel>
                  <Select
                    value={mutation.mutation || ''}
                    label="Mutation"
                    onChange={(e) => handleMutationChange(index, 'mutation', e.target.value)}
                  >
                    {mutation.gene && MUTATION_OPTIONS[mutation.gene]?.map((mut: string) => (
                      <MenuItem key={mut} value={mut}>{mut}</MenuItem>
                    ))}
                  </Select>
                </FormControl>
              </Grid>
              <Grid item xs={12} sm={6} md={3}>
                <FormControl fullWidth size="small">
                  <InputLabel>Origin</InputLabel>
                  <Select
                    value={mutation.origin || ''}
                    label="Origin"
                    onChange={(e) => handleMutationChange(index, 'origin', e.target.value)}
                  >
                    {ORIGIN_OPTIONS.map((origin) => (
                      <MenuItem key={origin} value={origin}>{origin}</MenuItem>
                    ))}
                  </Select>
                </FormControl>
              </Grid>
              <Grid item xs={12} sm={6} md={3}>
                <FormControl fullWidth size="small">
                  <InputLabel>Interpretation</InputLabel>
                  <Select
                    value={mutation.interpretation || ''}
                    label="Interpretation"
                    onChange={(e) => handleMutationChange(index, 'interpretation', e.target.value)}
                  >
                    {INTERPRETATION_OPTIONS.map((interp) => (
                      <MenuItem key={interp} value={interp}>{interp}</MenuItem>
                    ))}
                  </Select>
                </FormControl>
              </Grid>
            </Grid>
          </Box>
        ))}
        
        {(!editedInfo.genetic_mutations || editedInfo.genetic_mutations.length === 0) && (
          <Typography variant="body2" color="text.secondary" sx={{ fontStyle: 'italic', textAlign: 'center', py: 2 }}>
            No genetic mutations identified. Click "Add Mutation" to add one.
          </Typography>
        )}
      </Grid>
    </Grid>
  );

  const renderLymphomaTab = () => (
    <Grid container spacing={3}>
      <Grid item xs={12}>
        <Typography variant="h6" gutterBottom>Disease Characteristics</Typography>
      </Grid>
      {renderTextField('Histologic Subtype', 'histologic_type', true)}
      {renderSelectField('Ann Arbor Stage', 'stage', STAGE_OPTIONS)}
      {renderTextField('FLIPI Score', 'flipi_score', false, 'number')}
      {renderSelectField('FLIPI Risk Category', 'flipi_risk_category', FLIPI_RISK_OPTIONS)}
      {renderSelectField('Bulky Disease', 'bulky_disease', YES_NO_OPTIONS)}
      {renderSelectField('B Symptoms', 'b_symptoms', YES_NO_OPTIONS)}
      
      <Grid item xs={12}>
        <Divider sx={{ my: 2 }} />
        <Typography variant="h6" gutterBottom sx={{ mt: 2 }}>
          Laboratory Markers
        </Typography>
      </Grid>
      {renderTextField('LDH Level (U/L)', 'ldh_level', false, 'number')}
      {renderTextField('Beta-2 Microglobulin (mg/L)', 'beta2_microglobulin', false, 'number')}
      {renderSelectField('Bone Marrow Involvement', 'bone_marrow_involvement', YES_NO_OPTIONS)}
      {renderTextField('Number of Nodal Sites', 'number_of_nodal_sites', false, 'number')}
    </Grid>
  );

  const renderMyelomaTab = () => (
    <Grid container spacing={3}>
      <Grid item xs={12}>
        <Typography variant="h6" gutterBottom>Disease Characteristics</Typography>
      </Grid>
      {renderTextField('Myeloma Type', 'myeloma_type')}
      {renderSelectField('ISS Stage', 'stage', ISS_STAGE_OPTIONS)}
      {renderSelectField('R-ISS Stage', 'r_iss_stage', ISS_STAGE_OPTIONS)}
      {renderTextField('Durie-Salmon Stage', 'durie_salmon_stage')}
      
      <Grid item xs={12}>
        <Divider sx={{ my: 2 }} />
        <Typography variant="h6" gutterBottom sx={{ mt: 2 }}>
          Myeloma Markers
        </Typography>
      </Grid>
      {renderTextField('M-Protein Type', 'm_protein_type')}
      {renderTextField('Serum M-Protein (g/dL)', 'serum_m_protein', false, 'number')}
      {renderTextField('Urine M-Protein (mg/24h)', 'urine_m_protein', false, 'number')}
      {renderTextField('Free Light Chain Ratio', 'free_light_chain_ratio', false, 'number')}
      {renderTextField('Beta-2 Microglobulin (mg/L)', 'beta2_microglobulin', false, 'number')}
      {renderTextField('LDH Level (U/L)', 'ldh_level', false, 'number')}
      
      <Grid item xs={12}>
        <Divider sx={{ my: 2 }} />
        <Typography variant="h6" gutterBottom sx={{ mt: 2 }}>
          Complications
        </Typography>
      </Grid>
      {renderSelectField('Bone Lesions', 'bone_lesions', YES_NO_OPTIONS)}
      {renderSelectField('Hypercalcemia', 'hypercalcemia', YES_NO_OPTIONS)}
      {renderSelectField('Renal Impairment', 'renal_impairment', YES_NO_OPTIONS)}
      {renderSelectField('Anemia', 'anemia', YES_NO_OPTIONS)}
      {renderTextField('Plasma Cell Percentage (%)', 'plasma_cell_percentage', false, 'number')}
      
      <Grid item xs={12}>
        <Divider sx={{ my: 2 }} />
        <Typography variant="h6" gutterBottom sx={{ mt: 2 }}>
          Cytogenetics
        </Typography>
      </Grid>
      {renderSelectField('Cytogenetic Risk', 'cytogenetic_risk', CYTOGENETIC_RISK_OPTIONS)}
      {renderTextField('Cytogenetic Abnormalities', 'cytogenetic_abnormalities', true)}
      {renderTextField('Genetic Mutations', 'genetic_mutations', true)}
    </Grid>
  );

  const renderDiseaseSpecificTab = () => {
    const diseaseType = getDiseaseType();
    switch (diseaseType) {
      case 'breast':
        return renderBreastCancerTab();
      case 'lymphoma':
        return renderLymphomaTab();
      case 'myeloma':
        return renderMyelomaTab();
      default:
        return (
          <Grid container spacing={3}>
            {renderSelectField('Disease', 'disease', DISEASE_OPTIONS)}
            {renderSelectField('Stage', 'stage', STAGE_OPTIONS)}
            {renderTextField('Histologic Type', 'histologic_type', true)}
            <Grid item xs={12}>
              <Typography variant="body2" color="text.secondary">
                Disease-specific fields are available for Breast Cancer, Follicular Lymphoma, and Multiple Myeloma.
              </Typography>
            </Grid>
          </Grid>
        );
    }
  };

  const age = editedInfo?.date_of_birth ? calculateAge(editedInfo.date_of_birth) : null;

  return (
    <Box p={3}>
      <Box display="flex" justifyContent="space-between" alignItems="center" mb={3}>
        <Box display="flex" alignItems="center">
          <Button
            startIcon={<ArrowLeft size={20} />}
            onClick={() => navigate('/')}
            sx={{ mr: 2 }}
          >
            Back to Patient List
          </Button>
          <Typography variant="h4">
            {patientName} - Patient ID: {personId}
          </Typography>
        </Box>
        <Button
          variant="contained"
          startIcon={<Save size={20} />}
          onClick={handleSave}
          disabled={saving}
        >
          {saving ? 'Saving...' : 'Save Changes'}
        </Button>
      </Box>

      {error && (
        <Alert severity="error" sx={{ mb: 2 }}>
          {error}
        </Alert>
      )}

      {successMessage && (
        <Alert severity="success" sx={{ mb: 2 }}>
          {successMessage}
        </Alert>
      )}

      <Paper>
        <Tabs value={activeTab} onChange={handleTabChange} sx={{ borderBottom: 1, borderColor: 'divider' }}>
          <Tab label="General" />
          <Tab label={getDiseaseTabLabel()} />
          <Tab label="Treatment" />
          <Tab label="Blood" />
          <Tab label="Labs" />
          <Tab label="Behavior" />
        </Tabs>

        <TabPanel value={activeTab} index={0}>
          <Grid container spacing={3}>
            <Grid item xs={12} md={6}>
              <TextField
                fullWidth
                label="Patient Name"
                value={editedName}
                onChange={(e) => setEditedName(e.target.value)}
                variant="outlined"
                size="small"
              />
            </Grid>
            {renderDateField('Date of Birth', 'date_of_birth')}
            <Grid item xs={12} md={6}>
              <TextField
                fullWidth
                label="Age"
                value={age || ''}
                variant="outlined"
                size="small"
                disabled
                helperText="Calculated from date of birth"
              />
            </Grid>
            {renderSelectField('Gender', 'gender', GENDER_OPTIONS)}
            
            <Grid item xs={12}>
              <Divider sx={{ my: 2 }} />
              <Typography variant="h6" gutterBottom sx={{ mt: 2 }}>
                Location
              </Typography>
            </Grid>
            
            {renderSelectField('Country', 'country', COUNTRY_OPTIONS)}
            <Grid item xs={12} sm={6}>
              <TextField
                fullWidth
                label="Postal Code / Zip Code"
                value={editedInfo.postal_code || ''}
                onChange={(e) => handleZipcodeChange(e.target.value)}
                variant="outlined"
                helperText="Enter 5-digit US zip code to auto-fill city and state"
              />
            </Grid>
            {renderTextField('City', 'city')}
            {editedInfo.country === 'United States' 
              ? renderSelectField('State', 'region', US_STATES)
              : renderTextField('Region/State', 'region')
            }
            
            <Grid item xs={12}>
              <Divider sx={{ my: 2 }} />
              <Typography variant="h6" gutterBottom sx={{ mt: 2 }}>
                Ethnicity
              </Typography>
            </Grid>
            
            {renderSelectField('Ethnicity', 'ethnicity', ETHNICITY_OPTIONS, true)}
            
            <Grid item xs={12}>
              <Divider sx={{ my: 2 }} />
              <Typography variant="h6" gutterBottom sx={{ mt: 2 }}>
                Clinical Summary
              </Typography>
            </Grid>
            
            {renderSelectField('Disease', 'disease', DISEASE_OPTIONS)}
            {renderSelectField('Stage', 'stage', STAGE_OPTIONS)}
            {renderTextField('Histologic Type', 'histologic_type', true)}
            {renderSelectField('ECOG Performance Status', 'ecog_performance_status', ECOG_OPTIONS)}
            {renderSelectField('Karnofsky Performance Score', 'karnofsky_performance_score', KARNOFSKY_OPTIONS)}
            
            <Grid item xs={12}>
              <Divider sx={{ my: 2 }} />
              <Typography variant="h6" gutterBottom sx={{ mt: 2 }}>
                Physical Measurements
              </Typography>
            </Grid>
            
            {renderTextField('Weight (kg)', 'weight', false, 'number')}
            {renderTextField('Height (cm)', 'height', false, 'number')}
            {renderTextField('BMI', 'bmi', false, 'number')}
            {renderTextField('Systolic Blood Pressure (mmHg)', 'systolic_blood_pressure', false, 'number')}
            {renderTextField('Diastolic Blood Pressure (mmHg)', 'diastolic_blood_pressure', false, 'number')}
            {renderTextField('Heart Rate (bpm)', 'heartrate', false, 'number')}
          </Grid>
        </TabPanel>

        <TabPanel value={activeTab} index={1}>
          {renderDiseaseSpecificTab()}
        </TabPanel>

        <TabPanel value={activeTab} index={2}>
          <Typography variant="h6" gutterBottom>Treatment History</Typography>
          <Grid container spacing={3}>
            {renderSelectField('Prior Therapy', 'prior_therapy', YES_NO_OPTIONS, false, true)}
            {renderTextField('Number of Prior Lines', 'therapy_lines_count', false, 'number', true)}
            {renderTextField('Relapse Count', 'relapse_count', false, 'number', true)}
            {renderSelectField('Refractory Status', 'refractory_status', REFRACTORY_STATUS_OPTIONS, true, true)}
            
            <Grid item xs={12}>
              <Divider sx={{ my: 2 }} />
              <Typography variant="h6" gutterBottom sx={{ mt: 2 }}>
                First Line Therapy
              </Typography>
            </Grid>
            {renderSelectField('First Line Therapy', 'first_line_therapy', getTherapyOptions('first'), true)}
            {renderDateField('First Line Date', 'first_line_date')}
            {renderSelectField('First Line Outcome', 'first_line_outcome', THERAPY_OUTCOME_OPTIONS)}
            
            <Grid item xs={12}>
              <Divider sx={{ my: 2 }} />
              <Typography variant="h6" gutterBottom sx={{ mt: 2 }}>
                Second Line Therapy
              </Typography>
            </Grid>
            {renderSelectField('Second Line Therapy', 'second_line_therapy', getTherapyOptions('second'), true)}
            {renderDateField('Second Line Date', 'second_line_date')}
            {renderSelectField('Second Line Outcome', 'second_line_outcome', THERAPY_OUTCOME_OPTIONS)}
            
            <Grid item xs={12}>
              <Divider sx={{ my: 2 }} />
              <Typography variant="h6" gutterBottom sx={{ mt: 2 }}>
                Later Line Therapy
              </Typography>
            </Grid>
            {renderSelectField('Later Line Therapy', 'later_therapy', getTherapyOptions('later'), true)}
            {renderDateField('Later Line Date', 'later_date')}
            {renderSelectField('Later Line Outcome', 'later_outcome', THERAPY_OUTCOME_OPTIONS)}
            
            <Grid item xs={12}>
              <Divider sx={{ my: 2 }} />
              <Typography variant="h6" gutterBottom sx={{ mt: 2 }}>
                Prior Treatments
              </Typography>
            </Grid>
            {renderSelectField('Prior Surgery', 'prior_surgery', YES_NO_OPTIONS)}
            {renderSelectField('Prior Radiation', 'prior_radiation', YES_NO_OPTIONS)}
            {renderSelectField('Prior Chemotherapy', 'prior_chemotherapy', YES_NO_OPTIONS)}
            {renderSelectField('Prior Hormone Therapy', 'prior_hormone_therapy', YES_NO_OPTIONS)}
            {renderSelectField('Prior Targeted Therapy', 'prior_targeted_therapy', YES_NO_OPTIONS)}
            {renderSelectField('Prior Immunotherapy', 'prior_immunotherapy', YES_NO_OPTIONS)}
            {renderSelectField('Prior Transplant', 'prior_transplant', YES_NO_OPTIONS)}
            {renderSelectField('Prior Proteasome Inhibitor', 'prior_proteasome_inhibitor', YES_NO_OPTIONS)}
            {renderSelectField('Prior Immunomodulatory Drug', 'prior_immunomodulatory_drug', YES_NO_OPTIONS)}
            {renderSelectField('Prior Anti-CD38 Antibody', 'prior_anti_cd38', YES_NO_OPTIONS)}
          </Grid>
        </TabPanel>

        <TabPanel value={activeTab} index={3}>
          <Typography variant="h6" gutterBottom>Blood Counts</Typography>
          <Grid container spacing={3}>
            {renderTextField('Hemoglobin (g/dL)', 'hemoglobin_level', false, 'number')}
            {renderTextField('Hematocrit (%)', 'hematocrit', false, 'number')}
            {renderTextField('White Blood Cell Count (10³/µL)', 'white_blood_cell_count', false, 'number')}
            {renderTextField('Red Blood Cell Count (10⁶/µL)', 'red_blood_cell_count', false, 'number')}
            {renderTextField('Platelet Count (10³/µL)', 'platelet_count', false, 'number')}
            {renderTextField('Absolute Neutrophil Count (10³/µL)', 'absolute_neutrophile_count', false, 'number')}
            {renderTextField('Absolute Lymphocyte Count (10³/µL)', 'absolute_lymphocyte_count', false, 'number')}
            {renderTextField('Absolute Monocyte Count (10³/µL)', 'absolute_monocyte_count', false, 'number')}
          </Grid>
        </TabPanel>

        <TabPanel value={activeTab} index={4}>
          <Typography variant="h6" gutterBottom>Laboratory Values</Typography>
          <Grid container spacing={3}>
            <Grid item xs={12}>
              <Typography variant="subtitle1" fontWeight="bold" gutterBottom sx={{ mt: 1 }}>
                Chemistry Panel
              </Typography>
            </Grid>
            {renderTextField('Serum Creatinine (mg/dL)', 'serum_creatinine_level', false, 'number')}
            {renderTextField('Blood Urea Nitrogen (mg/dL)', 'blood_urea_nitrogen', false, 'number')}
            {renderTextField('eGFR (mL/min/1.73m²)', 'egfr', false, 'number')}
            {renderTextField('Serum Sodium (mEq/L)', 'serum_sodium', false, 'number')}
            {renderTextField('Serum Potassium (mEq/L)', 'serum_potassium', false, 'number')}
            {renderTextField('Serum Calcium (mg/dL)', 'serum_calcium_level', false, 'number')}
            {renderTextField('Serum Albumin (g/dL)', 'albumin_level', false, 'number')}
            {renderTextField('Total Protein (g/dL)', 'total_protein', false, 'number')}
            
            <Grid item xs={12}>
              <Typography variant="subtitle1" fontWeight="bold" gutterBottom sx={{ mt: 2 }}>
                Liver Function Tests
              </Typography>
            </Grid>
            {renderTextField('AST (U/L)', 'liver_enzyme_levels_ast', false, 'number')}
            {renderTextField('ALT (U/L)', 'liver_enzyme_levels_alt', false, 'number')}
            {renderTextField('ALP (U/L)', 'liver_enzyme_levels_alp', false, 'number')}
            {renderTextField('Total Bilirubin (mg/dL)', 'serum_bilirubin_level_total', false, 'number')}
            {renderTextField('Direct Bilirubin (mg/dL)', 'serum_bilirubin_level_direct', false, 'number')}
            
            <Grid item xs={12}>
              <Typography variant="subtitle1" fontWeight="bold" gutterBottom sx={{ mt: 2 }}>
                Other Markers
              </Typography>
            </Grid>
            {renderTextField('LDH (U/L)', 'ldh_level', false, 'number')}
            {renderTextField('Beta-2 Microglobulin (mg/L)', 'beta2_microglobulin', false, 'number')}
            {renderTextField('C-Reactive Protein (mg/L)', 'c_reactive_protein', false, 'number')}
            {renderTextField('ESR (mm/hr)', 'esr', false, 'number')}
          </Grid>
        </TabPanel>

        <TabPanel value={activeTab} index={5}>
          <Typography variant="h6" gutterBottom>Lifestyle & Behavior</Typography>
          <Grid container spacing={3}>
            <Grid item xs={12}>
              <Typography variant="subtitle1" fontWeight="bold" gutterBottom sx={{ mt: 1 }}>
                Performance Status
              </Typography>
            </Grid>
            {renderSelectField('ECOG Performance Status', 'ecog_performance_status', ECOG_OPTIONS)}
            {renderSelectField('Karnofsky Performance Score', 'karnofsky_performance_score', KARNOFSKY_OPTIONS)}
            
            <Grid item xs={12}>
              <Divider sx={{ my: 2 }} />
              <Typography variant="subtitle1" fontWeight="bold" gutterBottom sx={{ mt: 2 }}>
                Lifestyle Factors
              </Typography>
            </Grid>
            {renderSelectField('Smoking Status', 'smoking_status', SMOKING_STATUS_OPTIONS)}
            {renderTextField('Pack Years (if applicable)', 'pack_years', false, 'number')}
            {renderSelectField('Alcohol Use', 'alcohol_use', ALCOHOL_USE_OPTIONS)}
            {renderTextField('Drinks per Week (if applicable)', 'drinks_per_week', false, 'number')}
            {renderSelectField('Exercise Frequency', 'exercise_frequency', EXERCISE_FREQUENCY_OPTIONS)}
            {renderTextField('Exercise Minutes per Week', 'exercise_minutes_per_week', false, 'number')}
            {renderSelectField('Diet Type', 'diet_type', DIET_TYPE_OPTIONS)}
            
            <Grid item xs={12}>
              <Divider sx={{ my: 2 }} />
              <Typography variant="subtitle1" fontWeight="bold" gutterBottom sx={{ mt: 2 }}>
                Sleep & Wellbeing
              </Typography>
            </Grid>
            {renderTextField('Average Sleep Hours per Night', 'sleep_hours_per_night', false, 'number')}
            {renderSelectField('Sleep Quality', 'sleep_quality', SLEEP_QUALITY_OPTIONS)}
            {renderSelectField('Stress Level', 'stress_level', STRESS_LEVEL_OPTIONS)}
            {renderSelectField('Social Support', 'social_support', SOCIAL_SUPPORT_OPTIONS)}
            
            <Grid item xs={12}>
              <Divider sx={{ my: 2 }} />
              <Typography variant="subtitle1" fontWeight="bold" gutterBottom sx={{ mt: 2 }}>
                Socioeconomic Factors
              </Typography>
            </Grid>
            {renderSelectField('Employment Status', 'employment_status', EMPLOYMENT_STATUS_OPTIONS)}
            {renderSelectField('Education Level', 'education_level', EDUCATION_LEVEL_OPTIONS)}
            {renderSelectField('Marital Status', 'marital_status', MARITAL_STATUS_OPTIONS)}
            {renderSelectField('Insurance Type', 'insurance_type', INSURANCE_TYPE_OPTIONS)}
            {renderTextField('Number of Dependents', 'number_of_dependents', false, 'number')}
            {renderTextField('Annual Household Income (USD)', 'annual_household_income', false, 'number')}
          </Grid>
        </TabPanel>
      </Paper>
    </Box>
  );
};

export default PatientDetail;