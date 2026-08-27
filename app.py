import os
from flask import Flask, render_template, request, redirect, session
from werkzeug.security import generate_password_hash, check_password_hash
import sqlite3
import pandas as pd
import joblib
from datetime import datetime
from dateutil.relativedelta import relativedelta
import schedule
import threading
import time
import smtplib
from email.mime.text import MIMEText
import math

app = Flask(__name__)
app.secret_key = os.environ.get("FLASK_SECRET_KEY", "dev-only-change-this-secret")

# Vercel's deployed filesystem is read-only except for /tmp.
# Keep writable runtime files (SQLite + inventory updates) in /tmp.
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
RUNTIME_DIR = os.path.join("/tmp", "inventory_management_system")
os.makedirs(RUNTIME_DIR, exist_ok=True)

DB_PATH = os.path.join(RUNTIME_DIR, "users.db")
SOURCE_INVENTORY_PATH = os.path.join(BASE_DIR, "inventory_data.csv")
RUNTIME_INVENTORY_PATH = os.path.join(RUNTIME_DIR, "inventory_data.csv")
MODEL_PATH = os.path.join(BASE_DIR, "Stock_prediction_model.pkl")
SALES_MONTHLY_PATH = os.path.join(BASE_DIR, "sales_monthly.csv")
RAW_SALES_PATH = os.path.join(BASE_DIR, "supermarket_sales.csv")

# Copy the read-only deployment inventory into the writable runtime area once.
# This lets the Update Inventory page work on Vercel during a warm instance.
if not os.path.exists(RUNTIME_INVENTORY_PATH):
    import shutil
    shutil.copyfile(SOURCE_INVENTORY_PATH, RUNTIME_INVENTORY_PATH)

# ==========================
# Initialize SQLite DB
# ==========================
def init_db():
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    cursor.execute("""CREATE TABLE IF NOT EXISTS users (
                      id INTEGER PRIMARY KEY AUTOINCREMENT,
                      username TEXT,
                      email TEXT UNIQUE,
                      gmail_password TEXT,
                      password TEXT
                      )""")
    conn.commit()
    conn.close()

init_db()

# ==========================
# Load ML Model & Data
# ==========================
model = joblib.load(MODEL_PATH)
inventory_df = pd.read_csv(RUNTIME_INVENTORY_PATH)

# Use a small pre-computed monthly sales dataset on Vercel instead of loading
# the original 44 MB raw sales file and doing a large groupby at every cold start.
if os.path.exists(SALES_MONTHLY_PATH):
    sales_monthly = pd.read_csv(SALES_MONTHLY_PATH, parse_dates=['Date'])
else:
    sales_data = pd.read_csv(
        RAW_SALES_PATH,
        usecols=['Product_ID', 'Product_Name', 'Category', 'Date', 'Units_Sold'],
        parse_dates=['Date']
    )
    sales_monthly = sales_data.groupby(
        ['Product_ID','Product_Name','Category', pd.Grouper(key='Date', freq='ME')]
    )['Units_Sold'].sum().reset_index()
    sales_monthly['Year'] = sales_monthly['Date'].dt.year
    sales_monthly['Month'] = sales_monthly['Date'].dt.month
    for lag in [1, 2, 3, 6]:
        sales_monthly[f'Lag_{lag}'] = sales_monthly.groupby('Product_ID')['Units_Sold'].shift(lag)
    sales_monthly.dropna(inplace=True)

if 'Product_ID' in inventory_df.columns:
    inventory_df['Product_ID'] = inventory_df['Product_ID'].astype(str)
if 'Product_ID' in sales_monthly.columns:
    sales_monthly['Product_ID'] = sales_monthly['Product_ID'].astype(str)

LOW_STOCK_THRESHOLD = 25

def safe_qty(val):
    try:
        if val is None or (isinstance(val, float) and math.isnan(val)):
            return 0
        return int(val)
    except:
        return 0

def get_all_users():
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    cursor.execute("SELECT username,email,gmail_password FROM users")
    users = cursor.fetchall()
    conn.close()
    return [{"username": u[0], "email": u[1], "gmail_password": u[2]} for u in users]

def predict_stock(product_id, prediction_year, prediction_month):
    product_sales = sales_monthly[sales_monthly['Product_ID'] == str(product_id)]
    if product_sales.empty:
        return None

    last_row = product_sales.iloc[-1]
    product_name = last_row['Product_Name']
    category = last_row['Category']

    lags = [last_row.get(f'Lag_{i}', 0) for i in [1,2,3,6]]
    X_new = pd.DataFrame([[*lags, prediction_year, prediction_month]],
                         columns=['Lag_1','Lag_2','Lag_3','Lag_6','Year','Month'])
    future_sales = float(model.predict(X_new)[0])

    current_stock_row = inventory_df[inventory_df['Product_ID'] == str(product_id)]
    current_stock = safe_qty(current_stock_row.iloc[0]['Stock_Quantity']) if not current_stock_row.empty else 0
    required_stock = max(0, future_sales - current_stock)

    return {
        'Product_ID': str(product_id),
        'Product_Name': product_name,
        'Category': category,
        'Predicted_Sales': int(round(future_sales)),
        'Current_Stock': int(round(current_stock)),
        'Required_Stock_to_Add': int(round(required_stock))
    }

# ==========================
# Gmail Alert Function
# ==========================
def send_gmail_alert(user, subject, message):
    sender_email = user["email"]
    sender_password = user["gmail_password"]
    msg = MIMEText(message, "plain")
    msg['Subject'] = subject
    msg['From'] = sender_email
    msg['To'] = sender_email
    try:
        with smtplib.SMTP_SSL('smtp.gmail.com', 465) as server:
            server.login(sender_email, sender_password)
            print(f" Gmail login successful for {sender_email}")
            server.send_message(msg)
            print(f" Email sent to {sender_email}")
    except Exception as e:
        print(f" Email failed for {sender_email}: {e}")

# ==========================
# Alert Functions
# ==========================
def low_stock_check():
    global inventory_df
    print(" Running Low Stock Check...")
    if inventory_df.empty:
        print(" Inventory empty")
        return

    out_of_stock, low_stock = [], []

    for _, row in inventory_df.iterrows():
        qty = safe_qty(row.get('Stock_Quantity', 0))
        pid = str(row.get('Product_ID', ''))
        pname = row.get('Product_Name', 'Unknown')
        if qty <= 0:
            out_of_stock.append(f"• {pname} (ID:{pid}) — OUT OF STOCK")
        elif qty < LOW_STOCK_THRESHOLD:
            low_stock.append(f"• {pname} (ID:{pid}) — {qty} units left")

    if not out_of_stock and not low_stock:
        print(" No low stock items found")
        return

    message = " LOW STOCK ALERT\n\n"
    if out_of_stock:
        message += " OUT OF STOCK ITEMS:\n" + "\n".join(out_of_stock) + "\n\n"
    if low_stock:
        message += " LOW STOCK ITEMS:\n" + "\n".join(low_stock)

    print(" Low stock alert triggered")
    for user in get_all_users():
        send_gmail_alert(user, "Inventory Low Stock Alert", message)

def end_of_day_report():
    global inventory_df
    print(" Running Daily Stock Report...")
    if inventory_df.empty:
        print(" Inventory empty")
        return

    today = datetime.today().strftime("%Y-%m-%d")
    message = f" DAILY STOCK REPORT – {today}\n\n"
    for _, row in inventory_df.iterrows():
        qty = safe_qty(row.get('Stock_Quantity', 0))
        message += f"• {row['Product_Name']} (ID:{row['Product_ID']}) — {qty} units\n"

    print(" Sending daily report emails...")
    for user in get_all_users():
        send_gmail_alert(user, f"Daily Stock Report – {today}", message)

def monthly_prediction_report():
    global inventory_df
    print(" Running Monthly Stock Forecast...")
    if inventory_df.empty:
        print(" Inventory empty")
        return

    next_month_date = datetime.today() + relativedelta(months=1)
    next_month = next_month_date.month
    next_year = next_month_date.year
    message = f" MONTHLY STOCK FORECAST – {next_month}/{next_year}\n\n"

    for pid in inventory_df['Product_ID'].astype(str):
        forecast = predict_stock(pid, next_year, next_month)
        if forecast:
            message += f"• {forecast['Product_Name']} (ID:{pid}) → Need {forecast['Required_Stock_to_Add']} units\n"

    print(" Sending monthly forecast emails...")
    for user in get_all_users():
        send_gmail_alert(user, f"Monthly Stock Forecast – {next_month}/{next_year}", message)

# ==========================
# Scheduler
# ==========================
def run_scheduler():
    schedule.every(30).seconds.do(low_stock_check)
    schedule.every().day.at("22:57").do(end_of_day_report)
    schedule.every().day.at("22:58").do(monthly_prediction_report)
    while True:
        schedule.run_pending()
        time.sleep(1)

# ==========================
# Flask Routes
# ==========================
@app.route("/")
def index():
    if 'user' not in session:
        return redirect('/intro')
    return render_template("Main.html", username=session['user']['username'])

@app.route('/signup', methods=['GET','POST'])
def signup():
    if request.method == 'POST':
        username = request.form['username']
        email = request.form['email']
        gmail_password = request.form['gmail_password']
        password = generate_password_hash(request.form['password'])
        conn = sqlite3.connect(DB_PATH)
        cursor = conn.cursor()
        try:
            cursor.execute("INSERT INTO users (username,email,gmail_password,password) VALUES (?,?,?,?)",
                           (username,email,gmail_password,password))
            conn.commit()
        except sqlite3.IntegrityError:
            conn.close()
            return "Email already exists"
        conn.close()
        return redirect('/login')
    return render_template('signup.html')

@app.route('/login', methods=['GET','POST'])
def login():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        conn = sqlite3.connect(DB_PATH)
        cursor = conn.cursor()
        cursor.execute("SELECT * FROM users WHERE username=?", (username,))
        user = cursor.fetchone()
        conn.close()
        if user and check_password_hash(user[4], password):
            session['user'] = {"id": user[0], "username": user[1], "email": user[2], "gmail_password": user[3]}
            return redirect('/')
        else:
            return "Invalid credentials"
    return render_template('login.html')

@app.route('/logout')
def logout():
    session.pop('user', None)
    return redirect('/login')

@app.route('/manual_prediction', methods=['GET','POST'])
def manual_prediction():
    if 'user' not in session:
        return redirect('/login')
    forecast = None
    if request.method=='POST':
        product_id = str(request.form['product_id'])
        month = int(request.form['month'])
        year = int(request.form['year'])
        forecast = predict_stock(product_id, year, month)
    return render_template("manual_prediction.html", forecast=forecast, username=session['user']['username'])

@app.route('/add_inventory', methods=['GET','POST'])
def add_inventory():
    if 'user' not in session:
        return redirect('/login')
    if request.method=='POST':
        product_id = str(request.form['product_id'])
        change = int(request.form['change'])
        global inventory_df
        idx = inventory_df[inventory_df['Product_ID'].astype(str) == product_id].index
        if not idx.empty:
            inventory_df.loc[idx, 'Stock_Quantity'] = inventory_df.loc[idx, 'Stock_Quantity'].apply(safe_qty) + change
            inventory_df.to_csv(RUNTIME_INVENTORY_PATH, index=False)
    return render_template("add_inventory.html", username=session['user']['username'])

@app.route('/dashboards')
def dashboards():
    if 'user' not in session:
        return redirect('/login')
    return render_template("dashboards.html", username=session['user']['username'])

@app.route('/instructions')
def instructions():
    return render_template('instructions.html')

@app.route('/main')
def main_page():
    return render_template('Main.html')

@app.route('/intro')
def intro():
    return render_template('intro.html')

@app.route('/health')
def health():
    return {"status": "ok", "model_loaded": model is not None}

# ==========================
# Run App
# ==========================
if __name__=="__main__":
    threading.Thread(target=run_scheduler, daemon=True).start()
    app.run(host="0.0.0.0", port=int(os.environ.get("PORT", 5000)), debug=False, use_reloader=False)

