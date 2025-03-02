import pandas as pd
from sqlalchemy import create_engine

# Database connection details
DATABASE_URL = "postgresql://postgres:1234@localhost:5432/retail_project"

# Establish connection
engine = create_engine(DATABASE_URL)

# Query to fetch data
query = """
SELECT 
    CustomerID, 
    SUM(Quantity * UnitPrice) AS TotalAmount, 
    COUNT(DISTINCT InvoiceNo) AS TotalTransactions
FROM retail_transactions
GROUP BY CustomerID
ORDER BY TotalAmount DESC
LIMIT 10;
"""

# Fetch data using pandas
df = pd.read_sql(query, engine)

# Display the data
print(df)

#Data Cleaning
df = df.dropna(subset = ['CustomerID'])
df['InvoiceData'] = pd.to_datetime(df['InvoiceData'])

