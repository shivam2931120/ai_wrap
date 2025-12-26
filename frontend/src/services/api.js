import axios from 'axios';

// Use relative URLs for production, localhost for development
const API_URL = process.env.NODE_ENV === 'production' ? '' : 'http://localhost:5000';

const api = {
  getModels: async () => {
    try {
      const response = await axios.get(`${API_URL}/api/models`);
      return response.data;
    } catch (error) {
      console.error('Error fetching models:', error);
      throw error;
    }
  },

  generate: async (prompt, model, maxTokens, showDebug) => {
    try {
      const response = await axios.post(`${API_URL}/api/generate`, {
        prompt,
        model,
        max_tokens: maxTokens,
        show_debug: showDebug
      });
      return response.data;
    } catch (error) {
      if (error.response && error.response.data) {
        const errorData = error.response.data;
        const err = new Error(errorData.message || 'An error occurred');
        err.title = errorData.title;
        err.code = errorData.code;
        throw err;
      }
      throw new Error('Network error. Please check your connection.');
    }
  }
};

export default api;
