import apiClient from './client';
import type {
  Player,
  Zone,
  RegisterPlayerRequest,
  RegisterPlayerResponse,
  DailyLoginResponse,
} from '../types';

export const registerPlayer = async (
  telegram_id: number,
  username: string
): Promise<RegisterPlayerResponse> => {
  const request: RegisterPlayerRequest = { telegram_id, username };
  const response = await apiClient.post<RegisterPlayerResponse>('/players/register', request);
  return response.data;
};

export const getMe = async (): Promise<Player> => {
  const response = await apiClient.get<Player>('/players/me');
  return response.data;
};

export const getProfile = async (): Promise<Player> => {
  const response = await apiClient.get<Player>('/players/me/profile');
  return response.data;
};

export const dailyLogin = async (): Promise<DailyLoginResponse> => {
  const response = await apiClient.post<DailyLoginResponse>('/players/daily-login');
  return response.data;
};

export const getZones = async (): Promise<Zone[]> => {
  const response = await apiClient.get<Zone[]>('/zones/');
  return response.data;
};
