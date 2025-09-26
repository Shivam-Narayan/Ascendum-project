import API_BASE_URL from "../config";

const LiveDetectionApi = {
  /**
   * Generate a new batch ID for live detection
   * @returns {Promise<string>}
   */
  getLiveBatchId: async () => {
    const token = localStorage.getItem("token");

    const res = await fetch(`${API_BASE_URL}seamguard/detection/generate_batch_id/`, {
      method: "GET",
      headers: {
        Authorization: token ? `Bearer ${token}` : "",
      },
    });

    if (!res.ok) {
      const errText = await res.text();
      throw new Error(errText || "Failed to generate batch ID");
    }

    const data = await res.json();
    return data.batch_id;
  },

  /**
   * Send a frame for live defect detection
   * @param {string} batchId
   * @param {string} base64Image
   * @returns {Promise<Object>}
   */
  detectDefectLive: async (batchId, base64Image) => {
    const token = localStorage.getItem("token");

    const res = await fetch(`${API_BASE_URL}seamguard/detection/detect_defect_live/`, {
      method: "POST",
      headers: {
        "Content-Type": "application/json",
        Authorization: token ? `Bearer ${token}` : "",
      },
      body: JSON.stringify({
        batch_id: batchId,
        image: base64Image,
      }),
    });

    if (!res.ok) {
      const errText = await res.text();
      throw new Error(errText || "Failed to detect defect");
    }

    const data = await res.json();
    return data;
  },

  /**
   * Stop the live detection session and get final results
   * @param {string} batchId
   * @returns {Promise<Object>}
   */
  stopLiveDetection: async (batchId) => {
    const token = localStorage.getItem("token");

    const url = new URL(`${API_BASE_URL}seamguard/detection/stop_live_detection/`);
    url.searchParams.append("batch_id", batchId);

    const res = await fetch(url, {
      method: "GET",
      headers: {
        Authorization: token ? `Bearer ${token}` : "",
      },
    });

    if (!res.ok) {
      const errText = await res.text();
      throw new Error(errText || "Failed to stop live detection");
    }

    const data = await res.json();
    return data;
  },
};

export default LiveDetectionApi;
