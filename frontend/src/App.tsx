import React from 'react';
import {
  BrowserRouter as Router,
  Routes,
  Route,
  Navigate,
} from 'react-router-dom';
import { ThemeProvider, createTheme } from '@mui/material/styles';
import CssBaseline from '@mui/material/CssBaseline';
import { Box, CircularProgress } from '@mui/material';
import { Login } from './components/Auth/Login';
import PatientList from './components/Patient/PatientList';
import PatientDetail from './components/Patient/PatientDetail';
import UploadFHIR from './components/Patient/UploadFHIR';
import UploadCSV from './components/Patient/UploadCSV';
import { useAuth } from './hooks/useAuth';

const theme = createTheme({
  palette: {
    primary: {
      main: '#1976d2',
    },
    secondary: {
      main: '#dc004e',
    },
  },
});

const AppRoutes: React.FC = () => {
  const { currentUser, loading: authLoading } = useAuth();

  if (authLoading) {
    return (
      <Box display="flex" justifyContent="center" alignItems="center" minHeight="100vh">
        <CircularProgress />
      </Box>
    );
  }

  return (
    <Routes>
      <Route path="/login" element={<Login />} />
      
      {/* Protected routes */}
      <Route
        path="/"
        element={
          currentUser ? <PatientList /> : <Navigate to="/login" replace />
        }
      />
      <Route
        path="/patient/:personId"
        element={
          currentUser ? <PatientDetail /> : <Navigate to="/login" replace />
        }
      />
      <Route
        path="/upload-fhir"
        element={
          currentUser ? <UploadFHIR /> : <Navigate to="/login" replace />
        }
      />
      <Route
        path="/upload-csv"
        element={
          currentUser ? <UploadCSV /> : <Navigate to="/login" replace />
        }
      />
      
      {/* Catch all - redirect to home */}
      <Route path="*" element={<Navigate to="/" replace />} />
    </Routes>
  );
};

const App: React.FC = () => {
  return (
    <ThemeProvider theme={theme}>
      <CssBaseline />
      <Router>
        <AppRoutes />
      </Router>
    </ThemeProvider>
  );
};

export default App;
