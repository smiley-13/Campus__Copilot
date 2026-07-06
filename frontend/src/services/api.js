const API_BASE_URL = 'http://localhost:8000/api';

export const chatWithAgent = async (message, endpoint = '/chat') => {
  try {
    const response = await fetch(`${API_BASE_URL}${endpoint}`, {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
        'X-Session-ID': 'browser-session-1' // Placeholder for future persistence
      },
      body: JSON.stringify({ message, user_id: 'browser-user' })
    });
    
    if (!response.ok) {
      throw new Error('Failed to communicate with agent');
    }
    
    return await response.json();
  } catch (error) {
    console.error('Agent API Error:', error);
    throw error;
  }
};
