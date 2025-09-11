# Streamlit App Setup

## 📦 Installation

1. Create and activate a Python environment (recommended):

   ```bash
   python -m venv venv
   source venv/bin/activate   # For Linux/Mac
   venv\Scripts\activate      # For Windows
   ```

2. Install the required dependencies:

   ```bash
   pip install streamlit streamlit-authenticator pyyaml transformers joblib numpy torch torchvision pillow opencv-python ultralytics streamlit-webrtc av scikit-learn
   ```

---

## ⚙️ Configuration

- Update **`app.py`** with any necessary file paths.  
- User credentials are stored in the **config file**.  
- You can add or modify usernames and passwords there.  

**Default login credentials:**
- Username: `jsmith`
- Password: `abc`

---

## ▶️ Running the App

Navigate to the project directory in your terminal and run:

```bash
streamlit run app.py
```

---

## 💡 Notes
- It’s recommended to run the app inside a Python virtual environment.  
- Ensure all file paths in `app.py` are correctly set before running.  
