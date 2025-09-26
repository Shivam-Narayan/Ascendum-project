import API_BASE_URL from "../config"; 

export const trainModel = async ({ industry, epochs, fromScratch }) => {
  try {
    const token = localStorage.getItem("adminToken");

    const res = await fetch(
      `${API_BASE_URL}seamguard/training/consolidate-and-train/`,
      {
        method: "POST",
        headers: {
          "Content-Type": "application/json",
          Authorization: `Bearer ${token}`,
        },
        body: JSON.stringify({
          industry,
          epochs: parseInt(epochs),
          from_scratch: fromScratch,
        }),
      }
    );

    if (!res.ok) {
      const errText = await res.text();
      throw new Error(errText || "Failed to train model");
    }

    const data = await res.json();
    return data;
  } catch (err) {
    throw err;
  }
};
