# Database Setup Guide

## Overview
This guide explains how to configure the database connection for the Load Balancer Observability Dashboard using secure environment variables.

## Prerequisites
- SQL Server or SQL Server Express installed
- ODBC Driver 17 for SQL Server (or compatible driver)
- Python 3.8+ with required packages installed

## Configuration Steps

### 1. Environment File Setup

Copy the environment template file to create your configuration:

```bash
cp .env.template .env
```

### 2. Configure Database Credentials

Edit the `.env` file with your actual database credentials:

```env
# SQL Server Database Configuration
DB_SERVER=YOUR_SERVER_NAME
DB_DATABASE=TrafficInsights
DB_AUTH_TYPE=Windows Authentication
DB_USERNAME=YOUR_DOMAIN\YOUR_USERNAME
DB_PASSWORD=
DB_DRIVER=ODBC Driver 17 for SQL Server

# Optional: Connection timeout settings
DB_CONNECTION_TIMEOUT=30
DB_COMMAND_TIMEOUT=30

# Application Settings
LOG_LEVEL=INFO
DATA_DIRECTORY=../data/
```

### 3. Authentication Types

#### Windows Authentication (Recommended)
```env
DB_AUTH_TYPE=Windows Authentication
DB_USERNAME=YOUR_DOMAIN\YOUR_USERNAME
DB_PASSWORD=
```

#### SQL Server Authentication
```env
DB_AUTH_TYPE=SQL Server
DB_USERNAME=your_sql_username
DB_PASSWORD=your_sql_password
```

### 4. Common Server Name Examples

- **SQL Server Express**: `YOUR_COMPUTER_NAME\SQLEXPRESS`
- **Default SQL Server**: `YOUR_COMPUTER_NAME` or `localhost`
- **Named Instance**: `YOUR_COMPUTER_NAME\INSTANCE_NAME`
- **Remote Server**: `server.domain.com` or `192.168.1.100`

### 5. Test Database Connection

Run the integration test to verify your configuration:

```bash
python test_integration.py
```

Look for these success messages:
- ✅ ODBC SQL Server Driver
- ✅ Database Schema

### 6. Security Best Practices

1. **Never commit `.env` files** - They are excluded in `.gitignore`
2. **Use Windows Authentication** when possible for better security
3. **Limit database permissions** to only what's needed
4. **Use strong passwords** for SQL Server authentication
5. **Enable SSL/TLS encryption** for remote connections

## Troubleshooting

### Common Issues

#### Connection Timeout
```
Error: Login timeout expired
```
**Solution**: Increase `DB_CONNECTION_TIMEOUT` in `.env`

#### Named Pipes Error
```
Error: Named Pipes Provider: Could not open a connection to SQL Server
```
**Solutions**:
- Verify SQL Server is running
- Check server name spelling
- Enable Named Pipes in SQL Server Configuration Manager

#### Authentication Failed
```
Error: Login failed for user
```
**Solutions**:
- Verify username and password
- Check SQL Server authentication mode
- Ensure user has database permissions

#### Driver Not Found
```
Error: [Microsoft][ODBC Driver Manager] Data source name not found
```
**Solution**: Install ODBC Driver 17 for SQL Server

### Testing Connection

Use this Python script to test your connection:

```python
from dotenv import load_dotenv
import os
import pyodbc

load_dotenv()

server = os.getenv('DB_SERVER')
database = os.getenv('DB_DATABASE')
driver = os.getenv('DB_DRIVER')

try:
    connection_string = (
        f"DRIVER={{{driver}}};"
        f"SERVER={server};"
        f"DATABASE={database};"
        "Trusted_Connection=yes;"
    )
    
    conn = pyodbc.connect(connection_string)
    print("✅ Database connection successful!")
    conn.close()
    
except Exception as e:
    print(f"❌ Database connection failed: {e}")
```

## Database Schema

The application will automatically create the required database and tables:

1. **Database**: `TrafficInsights`
2. **Tables**:
   - `RequestLogs` - HTTP request telemetry
   - `ServerMetrics` - Server performance data
   - `AnalyticsReports` - Generated analytics reports

## Support

For additional support:
- Check the main `README.md` file
- Review the `PROJECT_OVERVIEW.md` documentation
- Contact: fareschehidi28@gmail.com
