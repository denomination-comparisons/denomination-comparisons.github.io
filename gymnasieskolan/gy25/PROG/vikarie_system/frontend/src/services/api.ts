import axios from 'axios';
import { Substitute } from '../types';

const API_BASE_URL = process.env.REACT_APP_API_URL || 'http://localhost:8000';

export const api = axios.create({
  baseURL: API_BASE_URL,
});

export const getSubstitutes = async (): Promise<Substitute[]> => {
  const response = await api.get('/substitutes/');
  return response.data;
};

export const createSubstitute = async (substitute: Omit<Substitute, 'id'>): Promise<Substitute> => {
  const response = await api.post('/substitutes/', substitute);
  return response.data;
};
