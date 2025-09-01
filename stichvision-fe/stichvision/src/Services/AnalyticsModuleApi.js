import API_BASE_URL from '../config';

const getAuthHeader = () => {
  const token = localStorage.getItem('token');
  return {
    'Authorization': `Bearer ${token}`
  };
};

const handleResponse = async (response) => {
  if (!response.ok) {
    const error = await response.json();
    throw new Error(error.message || 'Request failed');
  }
  return await response.json();
};

export const fetchDefectsByDate = (date) => {
  return fetch(`${API_BASE_URL}seamguard/dashboard/defects_by_date/?date=${date}`, {
    headers: getAuthHeader()
  }).then(handleResponse);
};

export const fetchLoginDetails = () => {
  return fetch(`${API_BASE_URL}seamguard/dashboard/login_details/`, {
    headers: getAuthHeader()
  }).then(handleResponse);
};

export const fetchTotalAnnotatedImages = () => {
  return fetch(`${API_BASE_URL}seamguard/dashboard/total_annotated_images/`, {
    headers: getAuthHeader()
  }).then(handleResponse);
};