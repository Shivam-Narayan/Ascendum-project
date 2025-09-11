# ChatBot Backend

This is the backend for the **ChatBot** project, developed using **Python** and **Django REST Framework (DRF)**.

---

## Project Setup Instructions

Follow these steps to clone, configure, and run the backend project on your local machine.

---

### Step 1: Clone the Repository

Take a pull from the `main` branch of the `chatbot_dev_backend` repository:

```bash
git clone https://github.com/sourcebitsllc/Ascendum_demo.git
cd Ascendum_demo
git checkout chatbot_dev_backend (this is the main branch)

***NOTE***

Create your own child branch after taking pull from the main branch


### Step 2:  Add the .env File

# .env file

# Database Configuration
DB_NAME=your_database_name
DB_USER=your_database_user
DB_PASSWORD=your_database_password
DB_HOST=localhost
DB_PORT=5432


### Step 3: Update Your Database Credentials

Open the .env file and replace the placeholder values with your actual database credentials.


### Step 4: Run the Project

Make sure you're in the root directory where run.py is located, then run:

python run.py
