import pandas as pd
import numpy as np
from sqlalchemy import create_engine
from datetime import datetime
import matplotlib.pyplot as plt
import seaborn as sns

# --------------------------
# Step 1: Connect to PostgreSQL and Load Data
# --------------------------

def load_data_from_db():
    # Update this connection string as needed
    DATABASE_URL = "postgresql://postgres:1234@localhost:5432/retail_project"
    engine = create_engine(DATABASE_URL)
    
    # Query all rows from the retail_transactions table
    query = "SELECT * FROM retail_transactions;"
    df = pd.read_sql(query, engine)
    
    # Debug: Print column names to check what's available
    print("Available columns in DataFrame:", df.columns.tolist())
    return df

# --------------------------
# Step 2: Data Preprocessing
# --------------------------

def preprocess_data(df):
    # Check if CustomerID exists, if not try to find an alternative
    if 'CustomerID' not in df.columns:
        # Check for similar column names with different cases
        cols = df.columns.tolist()
        customer_cols = [col for col in cols if 'customer' in col.lower()]
        if customer_cols:
            print(f"CustomerID not found, using {customer_cols[0]} instead")
            df = df.rename(columns={customer_cols[0]: 'CustomerID'})
        else:
            # If no customer column exists, create a proxy based on InvoiceNo
            print("No customer identifier found, using InvoiceNo as proxy for CustomerID")
            df['CustomerID'] = df['InvoiceNo'].astype(str)
    
    # Ensure CustomerID is treated as a string
    df['CustomerID'] = df['CustomerID'].astype(str)
    
    # Convert Quantity and UnitPrice to numeric, if not already
    df['Quantity'] = pd.to_numeric(df['Quantity'], errors='coerce')
    df['UnitPrice'] = pd.to_numeric(df['UnitPrice'], errors='coerce')
    
    # Remove rows with missing CustomerID, negative Quantity or non-positive UnitPrice
    df = df.dropna(subset=['CustomerID'])
    df = df[df['Quantity'] > 0]
    df = df[df['UnitPrice'] > 0]
    
    # Convert InvoiceDate to datetime
    try:
        df['InvoiceDate'] = pd.to_datetime(df['InvoiceDate'])
    except Exception as e:
        df['InvoiceDate'] = pd.to_datetime(df['InvoiceDate'], format='%m/%d/%Y %H:%M', errors='coerce')
    df = df.dropna(subset=['InvoiceDate'])
    
    # Calculate the total value for each transaction
    df['TotalValue'] = df['Quantity'] * df['UnitPrice']
    
    return df

# --------------------------
# Step 3: Compute RFM Metrics
# --------------------------

def calculate_rfm(df):
    # Verify required columns exist
    required_cols = ['CustomerID', 'InvoiceDate', 'InvoiceNo', 'TotalValue']
    missing_cols = [col for col in required_cols if col not in df.columns]
    
    if missing_cols:
        raise ValueError(f"Missing required columns: {missing_cols}")
    
    # Set analysis date as the day after the last transaction in the dataset
    analysis_date = df['InvoiceDate'].max() + pd.Timedelta(days=1)
    print(f"Analysis date: {analysis_date}")
    print(f"Total transactions: {len(df)}")
    print(f"Total customers: {df['CustomerID'].nunique()}")
    
    # Group data by CustomerID to compute RFM metrics
    rfm = df.groupby('CustomerID').agg({
        'InvoiceDate': lambda x: (analysis_date - x.max()).days,  # Recency
        'InvoiceNo': lambda x: len(x.unique()),                  # Frequency
        'TotalValue': 'sum'                                      # Monetary
    })
    
    rfm.columns = ['Recency', 'Frequency', 'Monetary']
    print("\nRFM Metrics Summary:")
    print(rfm.describe())
    
    return rfm

# --------------------------
# Step 4: Create RFM Scores and Segmentation
# --------------------------

def score_and_segment_rfm(rfm, quantiles=5):
    # Create labels for quantiles
    r_labels = list(range(quantiles, 0, -1))  # For recency: lower recency gets higher score
    f_labels = list(range(1, quantiles + 1))   # For frequency: higher frequency gets higher score
    m_labels = list(range(1, quantiles + 1))   # For monetary: higher monetary gets higher score

    # Create quantile groups with error handling in case data is sparse
    try:
        r_groups = pd.qcut(rfm['Recency'], q=quantiles, labels=r_labels)
        f_groups = pd.qcut(rfm['Frequency'].rank(method='first'), q=quantiles, labels=f_labels)
        m_groups = pd.qcut(rfm['Monetary'].rank(method='first'), q=quantiles, labels=m_labels)
    except ValueError as e:
        print(f"Error in creating quantiles: {e}")
        print("Falling back to a 3-quantile system...")
        quantiles = 3
        r_labels = list(range(quantiles, 0, -1))
        f_labels = list(range(1, quantiles + 1))
        m_labels = list(range(1, quantiles + 1))
        r_groups = pd.qcut(rfm['Recency'], q=quantiles, labels=r_labels)
        f_groups = pd.qcut(rfm['Frequency'].rank(method='first'), q=quantiles, labels=f_labels)
        m_groups = pd.qcut(rfm['Monetary'].rank(method='first'), q=quantiles, labels=m_labels)
    
    rfm['R'] = r_groups.astype(int)
    rfm['F'] = f_groups.astype(int)
    rfm['M'] = m_groups.astype(int)
    rfm['RFM_Score'] = rfm['R'].astype(str) + rfm['F'].astype(str) + rfm['M'].astype(str)
    
    # Define a segmentation function based on RFM scores (customize as needed)
    def segment_rfm(row):
        # Example segmentation logic for a 5-quantile system:
        if quantiles == 5:
            r, f, m = row['R'], row['F'], row['M']
            if r >= 4 and f >= 4 and m >= 4:
                return 'Champions'
            elif (r >= 3 and f >= 3 and m >= 3) and (r + f + m >= 10):
                return 'Loyal Customers'
            elif (r >= 4 and f >= 2 and m >= 2) and (r + f + m >= 8):
                return 'Potential Loyalists'
            elif r >= 4 and f <= 2:
                return 'Recent Customers'
            elif r >= 3 and f <= 2 and m <= 2:
                return 'Promising'
            elif (r >= 3 and f >= 3) and m <= 2:
                return 'Need Attention'
            elif (r >= 2 and r <= 3) and (f >= 2 and f <= 3) and m <= 2:
                return 'About to Sleep'
            elif r <= 2 and (f >= 3 or m >= 3):
                return 'At Risk'
            elif r <= 1 and (f >= 4 or m >= 4):
                return 'Cannot Lose Them'
            elif r <= 2 and f <= 2 and m <= 3:
                return 'Hibernating'
            else:
                return 'Lost'
        else:
            # Simpler segmentation for a 3-quantile system
            r, f, m = row['R'], row['F'], row['M']
            if r == 3 and f == 3:
                return 'Champions'
            elif r == 3 and f == 2:
                return 'Potential Loyalists'
            elif r == 3 and f == 1:
                return 'Recent Customers'
            elif r == 2 and f == 3:
                return 'Loyal Customers'
            elif r == 2 and f == 2:
                return 'Need Attention'
            elif r == 2 and f == 1:
                return 'About to Sleep'
            elif r == 1 and f == 3:
                return 'At Risk'
            elif r == 1 and f == 2:
                return 'Cannot Lose Them'
            else:
                return 'Lost'
    
    rfm['Segment'] = rfm.apply(segment_rfm, axis=1)
    
    return rfm

# --------------------------
# Step 5: Analyze and Visualize Segmentation
# --------------------------

def analyze_segments(rfm):
    # Group by segment and calculate summary statistics
    segment_analysis = rfm.groupby('Segment').agg({
        'Recency': 'mean',
        'Frequency': 'mean',
        'Monetary': 'mean'
    })
    
    # Add count of customers per segment
    segment_counts = rfm['Segment'].value_counts()
    segment_analysis['Count'] = segment_counts
    
    segment_analysis = segment_analysis.sort_values(by='Monetary', ascending=False)
    segment_analysis['Percentage'] = segment_analysis['Count'] / segment_analysis['Count'].sum() * 100
    segment_analysis['Percentage'] = segment_analysis['Percentage'].round(2)
    
    print("\nRFM Segment Analysis:")
    print(segment_analysis)
    
    # Save results to CSV for further use or dashboard integration
    rfm.to_csv('rfm_customer_segments.csv', index=True)
    segment_analysis.to_csv('rfm_segment_analysis.csv')
    
    # Optional: Create visualizations
    try:
        plt.style.use('fivethirtyeight')
        # Bar plot for customer distribution across segments
        plt.figure(figsize=(12, 6))
        segment_counts = rfm['Segment'].value_counts().sort_values(ascending=False)
        ax = sns.barplot(x=segment_counts.index, y=segment_counts.values)
        plt.title('Customer Distribution Across Segments')
        plt.xlabel('Segment')
        plt.ylabel('Number of Customers')
        plt.xticks(rotation=45)
        for i, v in enumerate(segment_counts.values):
            ax.text(i, v + 5, str(v), ha='center')
        plt.tight_layout()
        plt.savefig('customer_distribution.png')
        
        # Bar plot for average monetary value by segment
        plt.figure(figsize=(12, 6))
        ax = sns.barplot(x=segment_analysis.index, y=segment_analysis['Monetary'])
        plt.title('Average Monetary Value by Segment')
        plt.xlabel('Segment')
        plt.ylabel('Average Monetary Value')
        plt.xticks(rotation=45)
        for i, v in enumerate(segment_analysis['Monetary']):
            ax.text(i, v + 5, f'${v:.2f}', ha='center')
        plt.tight_layout()
        plt.savefig('monetary_by_segment.png')
        
        # Pie chart for segment distribution
        plt.figure(figsize=(10, 10))
        plt.pie(segment_counts.values, labels=segment_counts.index, autopct='%1.1f%%', shadow=True, startangle=90)
        plt.axis('equal')
        plt.title('Segment Distribution')
        plt.tight_layout()
        plt.savefig('segment_distribution_pie.png')
        
        print("\nVisualizations have been saved as PNG files.")
    except ImportError:
        print("\nMatplotlib/Seaborn not installed; skipping visualizations.")
    except Exception as e:
        print(f"\nError creating visualizations: {e}")

# --------------------------
# Main Execution
# --------------------------

def main():
    try:
        # Step 1: Load data from PostgreSQL
        df = load_data_from_db()
        
        # Step 2: Preprocess the data
        df_clean = preprocess_data(df)
        
        # Step 3: Calculate RFM metrics
        rfm_metrics = calculate_rfm(df_clean)
        
        # Step 4: Score and segment the customers using RFM metrics
        rfm_result = score_and_segment_rfm(rfm_metrics, quantiles=5)
        
        # Step 5: Analyze and visualize the segmentation results
        analyze_segments(rfm_result)
        
    except Exception as e:
        print(f"Error in RFM analysis: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    main()