{{ config(materialized='table') }}

WITH base AS (
    SELECT 
        "CustomerID",
        SUM("Quantity" * "UnitPrice") AS "TotalAmount",
        COUNT(DISTINCT "InvoiceNo") AS "TotalTransactions"
    FROM {{ source('retail_project', 'retail_transactions') }}
    GROUP BY "CustomerID"
)
SELECT
    "CustomerID",
    "TotalAmount",
    "TotalTransactions",
    CASE 
        WHEN "TotalAmount" > 10000 THEN 'High Value'
        WHEN "TotalAmount" BETWEEN 5000 AND 10000 THEN 'Medium Value'
        ELSE 'Low Value'
    END AS "CustomerSegment"
FROM base
