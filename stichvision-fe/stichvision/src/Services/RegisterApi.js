import API_BASE_URL from '../config';

export const fetchEmployeeDetails = async (empId) => {
  try {
    const response = await fetch(`${API_BASE_URL}seamguard/register/employee/${empId}`);
    if (!response.ok) {
      throw new Error('Employee not found');
    }
    return await response.json();
  } catch (error) {
    console.error('Error fetching employee details:', error);
    throw error;
  }
};

export const registerEmployee = async (empId, password, confirmPassword) => {
  try {
    const response = await fetch(`${API_BASE_URL}seamguard/register/`, {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
      },
      body: JSON.stringify({
        emp_id: empId,
        password: password,
        confirm_password: confirmPassword,
      }),
    });

    if (!response.ok) {
      const errorData = await response.json();
      throw new Error(errorData.message || 'Registration failed');
    }

    return await response.json();
  } catch (error) {
    console.error('Error registering employee:', error);
    throw error;
  }
};