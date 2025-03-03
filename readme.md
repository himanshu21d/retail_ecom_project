# RETAIL360: End-to-End Customer Analytics Pipeline

![RETAIL360 Dashboard](visualizations/retail-performance-dashboard.png)

## Overview

RETAIL360 is an industry-grade, end-to-end retail data analytics solution that ingests the Online Retail Dataset into a PostgreSQL database, applies robust ETL processes and data quality transformations using Python and dbt, and performs advanced customer segmentation via RFM analysis. The project culminates in interactive, real-time dashboards built with Apache Superset, providing actionable insights into revenue trends, customer behavior, and market performance. Designed to be fully containerized using Docker Compose, RETAIL360 is an ideal portfolio piece demonstrating best practices in data engineering, analytics, and visualization.

## Features

- **Comprehensive Data Pipeline**: Full ETL workflow from raw data to actionable insights
- **RFM Customer Analysis**: Segment customers based on Recency, Frequency, and Monetary value
- **Interactive Dashboards**: Real-time visualization of key metrics and KPIs
- **Containerized Architecture**: Easily deployable with Docker and Docker Compose
- **Industry Best Practices**: Implements data quality checks, version control, and modular design

## Architecture

![RETAIL360 Architecture](visualizations/retail_architecture.png)

The solution consists of four main components:

1. **Data Sources**: Online Retail Dataset with transaction records
2. **Data Ingestion & Processing**: PostgreSQL database, ETL Pipeline, Data Quality Checks, dbt Transformations
3. **Analytics**: RFM Analysis (Recency, Frequency, Monetary) leading to Customer Segmentation
4. **Visualization**: Interactive dashboards displaying Customer Segments, Revenue Trends, Customer Return Rate, and Top Customers

## Tech Stack

- **Database**: PostgreSQL
- **ETL & Transformations**: Python, dbt (data build tool)
- **Containerization**: Docker, Docker Compose
- **Version Control**: Git, GitHub
- **Visualization**: Apache Superset
- **Data Quality**: dbt tests, Python validation scripts

## Installation

### Prerequisites

- Git
- Python 3.8+
- Docker and Docker Compose

### Steps

1. **Clone the Repository:**

```bash
git clone https://github.com/YourUsername/retail360.git
cd retail360
```

2. **Set Up a Virtual Environment:**

```bash
python3 -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
```

3. **Install Dependencies:**

```bash
pip install -r requirements.txt
```

4. **Docker & Docker Compose:** Ensure Docker is installed on your machine. Then, build and start the containers:

```bash
docker-compose build
docker-compose up -d
```

## Configuration

### Environment Variables

- `DATABASE_URL`: Connection string for PostgreSQL (e.g., `postgresql://postgres:1234@postgres:5432/retail_project`)
- `SUPERSET_SECRET_KEY`: A secure, custom secret key for Apache Superset (e.g., `mysecretkey`)

### Configuration Files

- `superset_config.py`: Contains custom Superset settings
- `.env` (optional): Can be used to store environment variables locally

### dbt Profiles

Ensure your `~/.dbt/profiles.yml` (or local dbt configuration) matches your PostgreSQL credentials and schema.

## Usage

### ETL Process

Run the ETL script to load and preprocess data:

```bash
python scripts/etl_load.py
```

### RFM Segmentation

Execute the RFM analysis:

```bash
python scripts/rfm_customer_seg.py
```

### Superset Dashboards

Access Superset at http://localhost:8088, log in with your admin credentials, and start creating or viewing dashboards.

### dbt Transformations

From the `dbt_project` folder:

```bash
dbt run
dbt test
```

## Data Sources

- **Online Retail Dataset**: Sourced from the UCI Machine Learning Repository, the dataset contains detailed retail transactions including invoice numbers, product codes, descriptions, quantities, unit prices, customer IDs, and transaction dates.
- **Internal Derived Tables**: The project also creates derived tables (e.g., customer_summary, rfm_customer_segments) through dbt transformations and Python scripts.

## Project Structure

```
retail360/
│
├── dbt_project/                # dbt models, tests, and configurations
│   ├── models/
│   │   └── customer_summary.sql
│   └── dbt_project.yml
│
├── scripts/                    # Python scripts for ETL and RFM analysis
│   ├── etl_load.py
│   ├── rfm_customer_seg.py
│   └── query_data.py           # (Optional) For querying the database
│
├── visualizations/             # Generated charts and dashboards screenshots
│   ├── superset_dashboard.png
│   └── rfm_segments.png
│
├── data/                       # Data files (e.g., Online Retail.xlsx)
│
├── Dockerfile                  # Docker configuration for building the ETL environment
├── docker-compose.yml          # Multi-container setup (PostgreSQL, ETL, RFM analysis, Superset)
├── requirements.txt            # Python dependencies
├── superset_config.py          # Custom configuration for Superset
├── .gitignore                  # Files and folders to ignore in Git
└── README.md                   # Project documentation (this file)
```

## Key Dashboards

The RETAIL360 solution includes several pre-built dashboards:

1. **Monthly Revenue Trend**: Track revenue performance over time
2. **Top Customers**: Identify and analyze your highest-value customers
3. **Revenue by Country**: Geographical distribution of sales
4. **Customer Return Rate**: Monitor customer retention metrics
5. **Average Order Value**: Track transaction value patterns

## Contributors

- **Primary Developer**: Himanshu Dhahana
- **Contributors**: List any team members or external contributors here
- **Acknowledgements**: Special thanks to the developers of Apache Superset, dbt, and all open-source tools used in this project

## License

This project is released under the **MIT License**. See the LICENSE file for details.

## Future Roadmap

- Integration with real-time data streams
- Machine learning models for purchase prediction
- Enhanced recommendation engine
- Mobile-optimized dashboard views
