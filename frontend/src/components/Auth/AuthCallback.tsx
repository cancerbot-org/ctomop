import React, { useEffect, useState } from 'react';
import { useNavigate, useLocation } from 'react-router-dom';
import { Box, CircularProgress, Typography } from '@mui/material';
import api from '../../api/axios';

export const AuthCallback: React.FC = () => {
  const navigate = useNavigate();
  const location = useLocation();
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    const handleCallback = async () => {
      try {
        // Get the current URL parameters
        const urlParams = new URLSearchParams(location.search);
        const code = urlParams.get('code');
        const state = urlParams.get('state');

        if (!code) {
          setError('No authorization code received');
          setTimeout(() => navigate('/login'), 2000);
          return;
        }

        // Exchange the code for a session (backend handles this)
        // Just verify we're authenticated now
        const response = await api.get('/user/');
        
        if (response.data && response.data.user) {
          // Successfully authenticated, redirect to main page
          navigate('/', { replace: true });
        } else {
          setError('Authentication failed');
          setTimeout(() => navigate('/login'), 2000);
        }
      } catch (err: any) {
        console.error('Auth callback error:', err);
        setError(err.response?.data?.error || 'Authentication failed');
        setTimeout(() => navigate('/login'), 2000);
      }
    };

    handleCallback();
  }, [navigate, location]);

  if (error) {
    return (
      <Box display="flex" flexDirection="column" alignItems="center" justifyContent="center" minHeight="100vh">
        <Typography color="error" variant="h6">{error}</Typography>
        <Typography variant="body2" mt={2}>Redirecting to login...</Typography>
      </Box>
    );
  }

  return (
    <Box display="flex" flexDirection="column" alignItems="center" justifyContent="center" minHeight="100vh">
      <CircularProgress size={60} />
      <Typography variant="h6" mt={2}>Completing authentication...</Typography>
    </Box>
  );
};