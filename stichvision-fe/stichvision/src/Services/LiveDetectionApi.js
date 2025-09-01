import axios from "axios";

const API_BASE = "http://localhost:8000/seamguard";

// Create an axios instance with default config
const apiClient = axios.create({
  baseURL: API_BASE,
});

// Add request interceptor to include the auth token
apiClient.interceptors.request.use(
  (config) => {
    const token = localStorage.getItem("token");
    if (token) {
      config.headers.Authorization = `Bearer ${token}`;
    }
    return config;
  },
  (error) => {
    return Promise.reject(error);
  }
);

const LiveDetectionApi = {
  /**
   * Generate a new batch ID for live detection
   * @returns {Promise<string>}
   */
  getLiveBatchId: async () => {
    const response = await apiClient.get("/detection/generate_batch_id/");
    return response.data.batch_id;
  },

  /**
   * Send a frame for live defect detection
   * @param {string} batchId
   * @param {string} base64Image
   * @returns {Promise<Object>}
   */
  detectDefectLive: async (batchId, base64Image) => {
    const response = await apiClient.post("/detection/detect_defect_live", {
      batch_id: batchId,
      image: base64Image,
    });
    return response.data;
  },

  /**
   * Stop the live detection session and get final results
   * @param {string} batchId
   * @returns {Promise<Object>}
   */
  stopLiveDetection: async (batchId) => {
    const response = await apiClient.get("/detection/stop_live_detection/", {
      params: { batch_id: batchId },
    });
    return response.data;
  },
};

export default LiveDetectionApi;