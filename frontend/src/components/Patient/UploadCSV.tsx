import React, { useState } from 'react';
import {
  Box,
  Button,
  Typography,
  Paper,
  Alert,
  CircularProgress,
  List,
  ListItem,
  ListItemText,
} from '@mui/material';
import { useNavigate } from 'react-router-dom';
import { Upload, ArrowLeft } from 'lucide-react';
import api from '../../api/axios';

const UploadCSV: React.FC = () => {
  const navigate = useNavigate();
  const [file, setFile] = useState<File | null>(null);
  const [uploading, setUploading] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [success, setSuccess] = useState<{ created_count: number; errors: string[] } | null>(null);

  const handleFileChange = (event: React.ChangeEvent<HTMLInputElement>) => {
    const selectedFile = event.target.files?.[0];
    if (selectedFile) {
      if (!selectedFile.name.endsWith('.csv')) {
        setError('Please select a CSV file');
        setFile(null);
        return;
      }
      setFile(selectedFile);
      setError(null);
      setSuccess(null);
    }
  };

  const handleUpload = async () => {
    if (!file) {
      setError('Please select a file');
      return;
    }

    try {
      setUploading(true);
      setError(null);

      const formData = new FormData();
      formData.append('file', file);

      const response = await api.post('/patient-info/upload_csv/', formData, {
        headers: {
          'Content-Type': 'multipart/form-data',
        },
      });

      setSuccess(response.data);
      setFile(null);

      // Reset file input
      const fileInput = document.getElementById('csv-file-input') as HTMLInputElement;
      if (fileInput) {
        fileInput.value = '';
      }

      // Navigate to patient list after 2 seconds
      setTimeout(() => {
        navigate('/');
      }, 2000);
    } catch (err: any) {
      setError(err.response?.data?.error || 'Failed to upload file');
    } finally {
      setUploading(false);
    }
  };

  return (
    <Box p={3}>
      <Box display="flex" alignItems="center" mb={3}>
        <Button
          startIcon={<ArrowLeft size={20} />}
          onClick={() => navigate('/')}
          sx={{ mr: 2 }}
        >
          Back to Patient List
        </Button>
        <Typography variant="h4">Upload CSV</Typography>
      </Box>

      <Paper sx={{ p: 3, maxWidth: 600 }}>
        <Typography variant="body1" paragraph>
          Upload a CSV file containing patient data. The CSV should include columns for
          person_id, phone_number, date_of_birth, disease, and other patient information.
        </Typography>

        <Box mt={3}>
          <input
            id="csv-file-input"
            type="file"
            accept=".csv"
            onChange={handleFileChange}
            style={{ display: 'none' }}
          />
          <label htmlFor="csv-file-input">
            <Button
              variant="outlined"
              component="span"
              startIcon={<Upload size={20} />}
              fullWidth
            >
              Select CSV File
            </Button>
          </label>

          {file && (
            <Box mt={2}>
              <Typography variant="body2" color="text.secondary">
                Selected file: {file.name} ({(file.size / 1024).toFixed(2)} KB)
              </Typography>
            </Box>
          )}
        </Box>

        {error && (
          <Alert severity="error" sx={{ mt: 2 }}>
            {error}
          </Alert>
        )}

        {success && (
          <Alert severity="success" sx={{ mt: 2 }}>
            <Typography variant="body2">
              Successfully imported {success.created_count} patient(s)
            </Typography>
            {success.errors.length > 0 && (
              <Box mt={1}>
                <Typography variant="body2" fontWeight="bold">
                  Errors:
                </Typography>
                <List dense>
                  {success.errors.map((err, idx) => (
                    <ListItem key={idx}>
                      <ListItemText primary={err} />
                    </ListItem>
                  ))}
                </List>
              </Box>
            )}
            <Typography variant="body2" mt={1}>
              Redirecting to patient list...
            </Typography>
          </Alert>
        )}

        <Box mt={3}>
          <Button
            variant="contained"
            onClick={handleUpload}
            disabled={!file || uploading}
            fullWidth
          >
            {uploading ? <CircularProgress size={24} /> : 'Upload CSV'}
          </Button>
        </Box>

        <Box mt={3}>
          <Typography variant="h6" gutterBottom>
            Expected CSV Format:
          </Typography>
          <Typography variant="body2" component="pre" sx={{ 
            backgroundColor: '#f5f5f5', 
            p: 2, 
            borderRadius: 1,
            overflow: 'auto',
            fontSize: '0.85rem'
          }}>
{`person_id,phone_number,date_of_birth,disease,year_of_birth
1000,555-1234,1970-01-01,Breast Cancer,1970
1001,555-5678,1980-05-15,Lung Cancer,1980`}
          </Typography>
        </Box>
      </Paper>
    </Box>
  );
};

export default UploadCSV;