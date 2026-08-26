import pandas as pd
from sklearn.model_selection import train_test_split
from sklearn.ensemble import RandomForestRegressor
from sklearn.metrics import mean_squared_error
import joblib
import numpy as np

# Load data
sales_data = pd.read_csv("supermarket_sales.csv")
inventory_data = pd.read_csv("inventory_data.csv")  # Column: Product_ID, Current_Stock
sales_data['Date'] = pd.to_datetime(sales_data['Date'])

# Aggregate monthly sales
sales_monthly = sales_data.groupby(
    ['Product_ID', 'Product_Name', 'Category', pd.Grouper(key='Date', freq='ME')]
)['Units_Sold'].sum().reset_index()

# Feature engineering
sales_monthly['Year'] = sales_monthly['Date'].dt.year
sales_monthly['Month'] = sales_monthly['Date'].dt.month

for lag in [1,2,3,6]:
    sales_monthly[f'Lag_{lag}'] = sales_monthly.groupby('Product_ID')['Units_Sold'].shift(lag)
sales_monthly.dropna(inplace=True)

X = sales_monthly[['Lag_1','Lag_2','Lag_3','Lag_6','Year','Month']]
y = sales_monthly['Units_Sold']

X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=42)

model = RandomForestRegressor(n_estimators=100, max_depth=10, random_state=42, n_jobs=2)
model.fit(X_train, y_train)

# Save clean model
joblib.dump(model, "Stock_prediction_model.pkl")
print("Model saved as Stock_prediction_model.pkl")

# RMSE
rmse = np.sqrt(mean_squared_error(y_test, model.predict(X_test)))
print("RMSE:", rmse)
