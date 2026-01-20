import React, { useState, useEffect } from 'react';
import {
  Box,
  Table,
  TableBody,
  TableCell,
  TableContainer,
  TableHead,
  TableRow,
  Paper,
  Button,
  Typography,
  CircularProgress,
  Alert,
  Checkbox,
  Dialog,
  DialogTitle,
  DialogContent,
  DialogContentText,
  DialogActions,
} from '@mui/material';
import { useNavigate } from 'react-router-dom';
import { Upload, FileText, Trash2 } from 'lucide-react';
import api from '../../api/axios';

interface Patient {
  person_id: number;
  patient_name: string;
  age: number | null;
  disease: string;
  stage: string;
  updated_at: string;
}

const PatientList: React.FC = () => {
  const navigate = useNavigate();
  const [patients, setPatients] = useState<Patient[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);
  const [selectedIds, setSelectedIds] = useState<Set<number>>(new Set());
  const [deleteDialogOpen, setDeleteDialogOpen] = useState(false);
  const [deleting, setDeleting] = useState(false);

  useEffect(() => {
    fetchPatients();
  }, []);

  const fetchPatients = async () => {
    try {
      setLoading(true);
      const response = await api.get('/patient-info/');
      setPatients(response.data);
      setError(null);
    } catch (err: any) {
      setError(err.response?.data?.error || 'Failed to fetch patients');
    } finally {
      setLoading(false);
    }
  };

  const handleSelectAll = (event: React.ChangeEvent<HTMLInputElement>) => {
    if (event.target.checked) {
      setSelectedIds(new Set(patients.map(p => p.person_id)));
    } else {
      setSelectedIds(new Set());
    }
  };

  const handleSelectOne = (personId: number) => {
    const newSelected = new Set(selectedIds);
    if (newSelected.has(personId)) {
      newSelected.delete(personId);
    } else {
      newSelected.add(personId);
    }
    setSelectedIds(newSelected);
  };

  const handleDeleteClick = () => {
    if (selectedIds.size > 0) {
      setDeleteDialogOpen(true);
    }
  };

  const handleDeleteConfirm = async () => {
    try {
      setDeleting(true);
      await api.delete('/patient-info/bulk_delete/', {
        data: { person_ids: Array.from(selectedIds) }
      });
      
      // Refresh the list
      await fetchPatients();
      setSelectedIds(new Set());
      setDeleteDialogOpen(false);
      setError(null);
    } catch (err: any) {
      setError(err.response?.data?.error || 'Failed to delete patients');
    } finally {
      setDeleting(false);
    }
  };

  const handleDeleteCancel = () => {
    setDeleteDialogOpen(false);
  };

  const handleUploadCSV = () => {
    navigate('/upload-csv');
  };

  const handleUploadFHIR = () => {
    navigate('/upload-fhir');
  };

  const handleRowClick = (personId: number) => {
    navigate(`/patient/${personId}`);
  };

  const formatDate = (dateString: string) => {
    if (!dateString) return 'N/A';
    try {
      const date = new Date(dateString);
      return date.toLocaleDateString();
    } catch {
      return 'Invalid Date';
    }
  };

  if (loading) {
    return (
      <Box display="flex" justifyContent="center" alignItems="center" minHeight="400px">
        <CircularProgress />
      </Box>
    );
  }

  const isAllSelected = patients.length > 0 && selectedIds.size === patients.length;
  const isIndeterminate = selectedIds.size > 0 && selectedIds.size < patients.length;

  return (
    <Box>
      <Box display="flex" justifyContent="space-between" alignItems="center" mb={3}>
        <Typography variant="h4">Patient Records</Typography>
        <Box display="flex" gap={2}>
          {selectedIds.size > 0 && (
            <Button
              variant="outlined"
              color="error"
              startIcon={<Trash2 size={20} />}
              onClick={handleDeleteClick}
            >
              Delete Records ({selectedIds.size})
            </Button>
          )}
          <Button
            variant="outlined"
            startIcon={<Upload size={20} />}
            onClick={handleUploadCSV}
          >
            Upload CSV
          </Button>
          <Button
            variant="contained"
            startIcon={<FileText size={20} />}
            onClick={handleUploadFHIR}
          >
            Upload FHIR
          </Button>
        </Box>
      </Box>

      {error && (
        <Alert severity="error" sx={{ mb: 2 }}>
          {error}
        </Alert>
      )}

      <TableContainer component={Paper}>
        <Table>
          <TableHead>
            <TableRow>
              <TableCell padding="checkbox">
                <Checkbox
                  indeterminate={isIndeterminate}
                  checked={isAllSelected}
                  onChange={handleSelectAll}
                />
              </TableCell>
              <TableCell>ID</TableCell>
              <TableCell>Name</TableCell>
              <TableCell>Age</TableCell>
              <TableCell>Disease</TableCell>
              <TableCell>Stage</TableCell>
              <TableCell>Last Updated</TableCell>
            </TableRow>
          </TableHead>
          <TableBody>
            {patients.length === 0 ? (
              <TableRow>
                <TableCell colSpan={7} align="center">
                  <Typography color="text.secondary" py={4}>
                    No patients found. Upload a CSV or FHIR file to get started.
                  </Typography>
                </TableCell>
              </TableRow>
            ) : (
              patients.map((patient) => (
                <TableRow
                  key={patient.person_id}
                  hover
                  sx={{ cursor: 'pointer' }}
                >
                  <TableCell padding="checkbox" onClick={(e) => e.stopPropagation()}>
                    <Checkbox
                      checked={selectedIds.has(patient.person_id)}
                      onChange={() => handleSelectOne(patient.person_id)}
                    />
                  </TableCell>
                  <TableCell onClick={() => handleRowClick(patient.person_id)}>
                    {patient.person_id}
                  </TableCell>
                  <TableCell onClick={() => handleRowClick(patient.person_id)}>
                    {patient.patient_name}
                  </TableCell>
                  <TableCell onClick={() => handleRowClick(patient.person_id)}>
                    {patient.age ?? 'N/A'}
                  </TableCell>
                  <TableCell onClick={() => handleRowClick(patient.person_id)}>
                    {patient.disease || 'N/A'}
                  </TableCell>
                  <TableCell onClick={() => handleRowClick(patient.person_id)}>
                    {patient.stage || 'N/A'}
                  </TableCell>
                  <TableCell onClick={() => handleRowClick(patient.person_id)}>
                    {formatDate(patient.updated_at)}
                  </TableCell>
                </TableRow>
              ))
            )}
          </TableBody>
        </Table>
      </TableContainer>

      {/* Delete Confirmation Dialog */}
      <Dialog
        open={deleteDialogOpen}
        onClose={handleDeleteCancel}
      >
        <DialogTitle>Confirm Delete</DialogTitle>
        <DialogContent>
          <DialogContentText>
            Are you sure you want to delete {selectedIds.size} patient record{selectedIds.size !== 1 ? 's' : ''}?
            This action cannot be undone.
          </DialogContentText>
        </DialogContent>
        <DialogActions>
          <Button onClick={handleDeleteCancel} disabled={deleting}>
            Cancel
          </Button>
          <Button
            onClick={handleDeleteConfirm}
            color="error"
            variant="contained"
            disabled={deleting}
          >
            {deleting ? <CircularProgress size={24} /> : 'Delete'}
          </Button>
        </DialogActions>
      </Dialog>
    </Box>
  );
};

export default PatientList;