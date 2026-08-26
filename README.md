📦 Inventory Management & Stock Prediction System

<p align="center">

<strong>{=html}A modern Flask-based Inventory Management System with
Machine Learning stock prediction, low-stock alerts, inventory updates,
and analytics.</strong>{=html}

</p>

<p align="center">

<a href="https://github.com/cit-23-02-0104-creator/Inventory-management-system">{=html}
<img src="https://img.shields.io/badge/GitHub-Repository-181717?style=for-the-badge&logo=github" alt="GitHub Repository">{=html}
</a>{=html}
<a href="https://github.com/cit-23-02-0104-creator/Inventory-management-system/issues">{=html}
<img src="https://img.shields.io/badge/Issues-GitHub-0A0A0A?style=for-the-badge&logo=github" alt="GitHub Issues">{=html}
</a>{=html}
<img src="https://img.shields.io/badge/Python-3.x-3776AB?style=for-the-badge&logo=python&logoColor=white" alt="Python">{=html}
<img src="https://img.shields.io/badge/Flask-3.x-000000?style=for-the-badge&logo=flask&logoColor=white" alt="Flask">{=html}
<img src="https://img.shields.io/badge/Machine%20Learning-Random%20Forest-2E7D32?style=for-the-badge" alt="Machine Learning">{=html}

</p>

🔗 Quick Links

Resource                            Link

📁 GitHub Repository                Open Repository

📥 Clone Repository                 Clone from GitHub

🐛 Issues                           Report an Issue

🌿 Main Branch                      View main

📄 Application                      app.py

📦 Dependencies                     requirements.txt

🤖 Model Training                   train_model.py

📌 Project Overview

The Inventory Management & Stock Prediction System is a web-based
application developed using Python, Flask, SQLite, Pandas, and Machine
Learning.

The system helps users manage inventory, monitor stock levels, predict
future product demand, and receive automated notifications when stock
becomes low or unavailable.

It combines traditional inventory management with a Random Forest
Regression model to provide data-driven stock forecasting.

🎯 Main Goals

Manage product inventory efficiently

Monitor low-stock and out-of-stock products

Predict future product sales

Estimate additional stock requirements

Provide a simple web-based dashboard

Send automated inventory notifications

Support data-driven business decisions

✨ Key Features

🔐 User Authentication

User registration

Secure password hashing

Login and logout

Session-based authentication

SQLite database for user records

📦 Inventory Management

View inventory data

Add or update stock quantities

Track product IDs and product names

Automatically save updated inventory data

🚨 Stock Monitoring

The application continuously checks inventory levels.

Out of Stock: 0 units

Low Stock: below 25 units

Automated low-stock checking

Email notification support

🤖 Machine Learning Stock Prediction

The system uses a Random Forest Regression model to forecast future
sales.

Model features include:

Lag_1

Lag_2

Lag_3

Lag_6

Year

Month

Target variable:

Units_Sold

The model is trained from historical sales data and stored as:

Stock_prediction_model.pkl

🔮 Manual Prediction

Users can select:

Product ID

Prediction month

Prediction year

The system returns:

Product name

Category

Predicted sales

Current stock

Required stock to add

📊 Analytics

The project supports analytics dashboards using Power BI files:

Sales analysis.pbix

Stock analysis.pbix

Power BI reports may require the correct sharing/embedding permissions
before they can be viewed by other users.

📧 Automated Email Reports

The application supports Gmail-based notifications for:

Low-stock alerts

Out-of-stock alerts

Daily stock reports

Monthly stock forecasts

For Gmail SMTP, use a Gmail App Password where required. Never commit
real passwords or secrets to GitHub.

🛠️ Technology Stack

Technology        Purpose

🐍 Python         Core programming language
🌐 Flask          Web application framework
🗄️ SQLite         User database
🐼 Pandas         Data processing
🔢 NumPy          Numerical operations
🤖 Scikit-learn   Machine Learning
💾 Joblib         ML model storage/loading
📧 SMTP / Gmail   Email notifications
📊 Power BI       Data visualization
🚀 Gunicorn       Production WSGI server
🎨 HTML/CSS       Frontend

📂 Project Structure

Inventory-management-system/
│
├── app.py
├── train_model.py
├── requirements.txt
├── Procfile
├── .env.example
├── .gitignore
│
├── inventory_data.csv
├── supermarket_sales.csv
├── Stock_prediction_model.pkl
│
├── templates/
│   ├── index.html
│   ├── intro.html
│   ├── Main.html
│   ├── login.html
│   ├── signup.html
│   ├── add_inventory.html
│   ├── manual_prediction.html
│   ├── dashboards.html
│   └── instructions.html
│
├── static/
│   ├── css/
│   └── images/
│
├── Sales analysis.pbix
├── Stock analysis.pbix
│
└── README.md

🚀 Getting Started

1️⃣ Clone the Repository

Open Command Prompt / PowerShell / Terminal and run:

git clone https://github.com/cit-23-02-0104-creator/Inventory-management-system.git

Then enter the project folder:

cd Inventory-management-system

You can also open the repository directly:

👉
https://github.com/cit-23-02-0104-creator/Inventory-management-system

2️⃣ Create a Virtual Environment

Windows PowerShell

python -m venv .venv
.\.venv\Scripts\Activate.ps1

Windows CMD

python -m venv .venv
.venv\Scripts\activate

macOS / Linux

python3 -m venv .venv
source .venv/bin/activate

3️⃣ Install Dependencies

pip install -r requirements.txt

If pip is not recognized, try:

python -m pip install -r requirements.txt

4️⃣ Configure Environment Variables

Create a .env file based on .env.example.

Example:

FLASK_SECRET_KEY=your-long-random-secret-key

Windows PowerShell

$env:FLASK_SECRET_KEY="your-long-random-secret-key"

macOS / Linux

export FLASK_SECRET_KEY="your-long-random-secret-key"

⚠️ Do not upload your real .env file to GitHub.

5️⃣ Run the Application

python app.py

When the server starts, open:

🏠 Application

http://127.0.0.1:5000

❤️ Health Check

http://127.0.0.1:5000/health

The health endpoint should return a response similar to:

{
  "status": "ok",
  "model_loaded": true
}

🌐 Application Routes

After starting Flask, these routes are available:

Page                    Local Link                                        Purpose

🏠 Home                 Open                    Main application

👋 Intro                Open               Introduction page

🔑 Login                Open               User login

📝 Signup               Open              Create account

📦 Add Inventory        Open       Update stock

🔮 Prediction           Open   Manual stock prediction

📊 Dashboards           Open          Analytics dashboards

📖 Instructions         Open        System instructions

❤️ Health               Open              Application health
status

🚪 Logout               /logout                                         Logout from the system

Note: The local links above work after the Flask application is
running on port 5000.

🧠 Machine Learning Workflow

The prediction pipeline follows these steps:

Historical Sales Data
        ↓
Data Cleaning
        ↓
Monthly Sales Aggregation
        ↓
Lag Feature Creation
        ↓
Random Forest Regression
        ↓
Future Sales Prediction
        ↓
Compare with Current Stock
        ↓
Required Stock Calculation

Training Features

Lag_1
Lag_2
Lag_3
Lag_6
Year
Month

Prediction Output

Predicted Sales
Current Stock
Required Stock to Add

🔄 Retrain the Model

If you update the sales dataset and want to train the model again:

python train_model.py

The trained model will be saved as:

Stock_prediction_model.pkl

You can review the training script here:

👉 train_model.py on
GitHub

📧 Gmail Email Alerts

The application can send email notifications using Gmail SMTP.

The system can generate:

🚨 Low Stock Alert

Sent when products fall below the configured threshold.

❌ Out of Stock Alert

Sent when a product reaches 0 units.

📅 Daily Stock Report

Contains current stock levels for products.

📈 Monthly Stock Forecast

Provides predicted stock requirements for the upcoming month.

🔐 Gmail Security

Do not store real Gmail passwords directly in source code.

For Gmail SMTP authentication, use a dedicated App Password where
applicable.

⏰ Automated Scheduler

The application includes scheduled background tasks.

Current scheduling configuration:

Low-stock check       → Every 30 seconds
Daily stock report    → 22:57
Monthly forecast      → 22:58

These schedules are configured inside app.py.

For production deployments, make sure the hosting environment supports
long-running background processes.

☁️ Deployment

The project includes a Procfile and Gunicorn configuration.

Production start command:

gunicorn app:app

The application also supports the PORT environment variable.

Example:

PORT=5000

Deployment Files

Procfile

requirements.txt

.env.example

🔒 Security

Please never commit the following to GitHub:

.env
users.db
Real Gmail passwords
Gmail App Passwords
API keys
Private credentials
Secret configuration files

Recommended practice:

.env.example  → Safe template
.env          → Local/private configuration
.gitignore    → Prevent secrets from being committed

The Flask secret key should always be replaced with a strong random
value in production.

🧪 Testing

The project includes an email testing script:

python test_email.py

Run tests only after configuring the required email credentials.

🐛 Troubleshooting

ModuleNotFoundError

Install the dependencies again:

pip install -r requirements.txt

Address already in use

Another application is using port 5000.

Stop the previous Flask process or use another port:

Windows PowerShell

$env:PORT="5001"
python app.py

Then open:

http://127.0.0.1:5001

Model loading error

Make sure this file exists in the application directory:

Stock_prediction_model.pkl

If necessary, regenerate it:

python train_model.py

CSV file not found

Make sure these files are available in the expected project directory:

inventory_data.csv
supermarket_sales.csv

📊 Power BI Dashboards

The project contains Power BI analytics resources for:

Sales analysis

Stock analysis

Inventory trends

Business insights

Files:

Sales analysis.pbix
Stock analysis.pbix

Power BI files may require Microsoft Power BI Desktop and the correct
data/report permissions.

👥 Contributors

This project is maintained in the GitHub repository:

👉
cit-23-02-0104-creator/Inventory-management-system

For contribution or issue reporting:

👉 Open GitHub
Issues

⭐ Support the Project

If you find this project useful:

⭐ Star the repository

🍴 Fork the project

🐛 Report bugs through Issues

💡 Suggest improvements

🔧 Submit a Pull Request

👉 Visit the GitHub
Repository

📜 License

If a specific license has not yet been added to the repository, treat
this project as all rights reserved by the project owner until a
license is explicitly provided.

<p align="center">

<strong>{=html}📦 Inventory Management System • 🤖 ML Stock Prediction
• 📊 Analytics • 🚨 Smart Alerts</strong>{=html}

</p>
