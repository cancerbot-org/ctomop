import { useState, useEffect } from 'react';
import api from '../api/axios';

interface User {
  id: number;
  username: string;
  email: string;
  first_name: string;
  last_name: string;
}

export const useAuth = () => {
  const [currentUser, setCurrentUser] = useState<User | null>(null);
  const [loading, setLoading] = useState(true);

  const fetchCurrentUser = async () => {
    try {
      setLoading(true);
      const response = await api.get('/user/');
      const userData = response.data.user || response.data;
      setCurrentUser(userData);
      return userData;
    } catch (error: any) {
      console.error('Failed to fetch current user:', error);
      if (error.response?.status === 401) {
        setCurrentUser(null);
      }
      return null;
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    fetchCurrentUser();
  }, []);

  const login = async (username: string, password: string) => {
    try {
      const response = await api.post('/auth/login/', {
        username,
        password,
      });
      const userData = response.data.user;
      setCurrentUser(userData);
      return { success: true, user: userData };
    } catch (error: any) {
      console.error('Login failed:', error);
      return { 
        success: false, 
        error: error.response?.data?.error || 'Login failed' 
      };
    }
  };

  const logout = async () => {
    try {
      await api.post('/auth/logout/');
    } catch (error) {
      console.error('Logout failed:', error);
    } finally {
      setCurrentUser(null);
      window.location.href = '/login';
    }
  };

  const refresh = async () => {
    return fetchCurrentUser();
  };

  return { currentUser, loading, login, logout, refresh };
};