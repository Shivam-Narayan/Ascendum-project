import React, { useState } from "react";
import "./AdminTrainModel.css";
import { trainModel } from "../../../Services/AdminTrainModelApi";
import { toast, ToastContainer } from "react-toastify";
import "react-toastify/dist/ReactToastify.css";

function AdminTrainModel() {
  const [industry, setIndustry] = useState("Glass");
  const [epochs, setEpochs] = useState(1);
  const [fromScratch, setFromScratch] = useState(true);
  const [loading, setLoading] = useState(false);

  const handleTrain = async () => {
    // Validation
    if (!industry.trim()) {
      toast.error("Industry is required");
      return;
    }

    if (epochs < 1 || epochs > 1000) {
      toast.error("Epochs must be between 1 and 1000");
      return;
    }

    setLoading(true);

    try {
      const data = await trainModel({ industry, epochs, fromScratch });
      toast.success("Training completed successfully!");

      // Optional: show extra details
      if (data.model_path) toast.info(`Model saved at: ${data.model_path}`);
      if (data.training_time) toast.info(`Training Time: ${data.training_time}`);
    } catch (err) {
      const errorMessage =
        err.response?.data?.message ||
        err.message ||
        "Training failed. Please try again.";
      toast.error(`${errorMessage}`);
    } finally {
      setLoading(false);
    }
  };

  const handleReset = () => {
    setIndustry("Glass");
    setEpochs(1);
    setFromScratch(true);
    toast.info("Form has been reset");
  };

  return (
    <div className="adminTrain-container">
      <div className="adminTrain-header">
        <h2 className="adminTrain-title">Model Training</h2>
        <p className="adminTrain-subtitle">
          Train machine learning models for different industries
        </p>
      </div>

      <div className="adminTrain-card">
        <div className="adminTrain-form">
          <div className="adminTrain-formGroup">
            <label className="adminTrain-label">Industry</label>
            <select
              className="adminTrain-input adminTrain-select"
              value={industry}
              onChange={(e) => setIndustry(e.target.value)}
              disabled={loading}
            >
              <option value="Glass">Glass</option>
              <option value="Metal">Metal</option>
              <option value="Plastic">Plastic</option>
              <option value="Textile">Textile</option>
              <option value="Other">Other</option>
            </select>
          </div>

          <div className="adminTrain-formGroup">
            <label className="adminTrain-label">Epochs</label>
            <input
              type="number"
              min="1"
              max="1000"
              className="adminTrain-input"
              value={epochs}
              onChange={(e) => setEpochs(parseInt(e.target.value) || 1)}
              disabled={loading}
            />
            <span className="adminTrain-hint">Recommended: 1-100 epochs</span>
          </div>

          <div className="adminTrain-formGroup adminTrain-checkboxGroup">
            <label className="adminTrain-checkboxLabel">
              <input
                type="checkbox"
                className="adminTrain-checkbox"
                checked={fromScratch}
                onChange={() => setFromScratch(!fromScratch)}
                disabled={loading}
              />
              <span className="adminTrain-checkboxCustom"></span>
              Train from scratch
            </label>
            <span className="adminTrain-hint">
              Uncheck to continue training from existing model
            </span>
          </div>

          <div className="adminTrain-buttonGroup">
            <button
              className="adminTrain-btn adminTrain-btnPrimary"
              onClick={handleTrain}
              disabled={loading}
            >
              {loading ? (
                <>
                  <span className="adminTrain-spinner"></span>
                  Training in Progress...
                </>
              ) : (
                "Start Training"
              )}
            </button>

            <button
              className="adminTrain-btn adminTrain-btnSecondary"
              onClick={handleReset}
              disabled={loading}
            >
              Reset
            </button>
          </div>
        </div>
      </div>

      {/* Toast notification container */}
      <ToastContainer position="top-right" autoClose={2500} hideProgressBar />
    </div>
  );
}

export default AdminTrainModel;
