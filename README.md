# Load Balancer Analytics at Hyperscale

[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)
[![Python 3.8+](https://img.shields.io/badge/python-3.8+-blue.svg)](https://www.python.org/downloads/)
[![SQL Server](https://img.shields.io/badge/database-SQL%20Server-red.svg)](https://www.microsoft.com/en-us/sql-server)

> **Enterprise-grade load balancer observability platform with ML-powered retry prediction, real-time analytics, SQL Server integration, and Power BI dashboards for high-scale traffic management.**

## 🚀 Quick Start

```bash
# Clone the repository
git clone https://github.com/FCHEHIDI/Load-Balancer-Analytics-at-Hyperscale.git
cd Load-Balancer-Analytics-at-Hyperscale

# Setup observability dashboard
cd load-balancer-observability-dashboard
pip install -r requirements.txt

# Configure database credentials
cp .env.template .env
# Edit .env with your SQL Server credentials

# Run the complete pipeline
python src/observability_orchestrator.py
```

## 📊 What's Included

### 🔍 Load Balancer Observability Dashboard
Real-time monitoring and analytics platform for load balancer infrastructure.

**Key Features:**
- Real-time telemetry processing and visualization
- Comprehensive KPI computation and anomaly detection
- SQL Server data warehousing with enterprise-grade performance
- Power BI dashboard integration for executive and operational views
- Automated alerting and notification systems

### 🤖 Load Balancer Retry Prediction
Machine learning solution for predicting client retry behavior.

**Key Features:**
- Predictive analytics for client retry patterns
- Production-ready API for real-time predictions
- Business impact analysis and ROI quantification
- Integration patterns for existing load balancer infrastructure
- Comprehensive model documentation and validation

## 🏗️ Architecture Overview

![Predictive Retry Modeling System](assets/retry_pipeline_illustration.png)

The system consists of two complementary components:

1. **Observability Dashboard** - Real-time monitoring and analytics
2. **Retry Prediction ML** - Predictive analytics for optimization

Both components work together to provide comprehensive load balancer analytics and intelligent optimization.

## 🔧 Configuration

### Database Setup
```bash
# 1. Configure your database credentials
cp load-balancer-observability-dashboard/.env.template load-balancer-observability-dashboard/.env

# 2. Edit the .env file with your SQL Server details
DB_SERVER=YOUR_SERVER_NAME
DB_DATABASE=TrafficInsights
DB_AUTH_TYPE=Windows Authentication
DB_USERNAME=YOUR_DOMAIN\YOUR_USERNAME
```

### Security Features
- ✅ Environment variables for all sensitive configuration
- ✅ `.env` file support with automatic loading
- ✅ No hardcoded credentials in source code
- ✅ Secure credential templates for easy setup
- ✅ Git ignore rules for sensitive files

## 🧪 Testing

Run the comprehensive integration test suite:

```bash
python test_integration.py
```

This validates:
- Python environment and dependencies
- Project structure and imports
- Database configuration
- Data generation and analytics
- File system permissions

## 📁 Project Structure

```
Load-Balancer-Analytics-at-Hyperscale/
├── 📊 load-balancer-observability-dashboard/    # Real-time monitoring platform
│   ├── src/                                     # Core application modules
│   ├── data/                                    # Generated telemetry data
│   ├── config/                                  # Database schema and configuration
│   ├── docs/                                    # Technical documentation
│   └── dashboards/                              # Power BI integration
├── 🤖 load-balancer-retry-prediction/          # ML prediction system
│   ├── src/                                     # ML model and API
│   ├── notebooks/                               # Jupyter analysis notebooks
│   ├── models/                                  # Trained ML models
│   └── examples/                                # Integration examples
├── 📄 PROJECT_OVERVIEW.md                       # Comprehensive project documentation
├── 🖼️ assets/                                   # Project images and diagrams
└── 🧪 test_integration.py                       # Integration test suite
```

## 💡 Use Cases

### Operations Team
- Real-time load balancer monitoring
- Performance optimization insights
- Incident response and troubleshooting
- Capacity planning and scaling decisions

### Development Team
- API integration for retry prediction
- Custom analytics and reporting
- Performance testing and validation
- Infrastructure automation

### Management Team
- Executive dashboards and KPI tracking
- ROI analysis and cost optimization
- Strategic infrastructure planning
- Business impact assessment

## 📖 Documentation

- **[Complete Project Overview](PROJECT_OVERVIEW.md)** - Comprehensive documentation
- **[Database Setup Guide](load-balancer-observability-dashboard/DATABASE_SETUP.md)** - Configuration instructions
- **[Architecture Overview](load-balancer-observability-dashboard/docs/architecture_overview.md)** - Technical architecture
- **[Dashboard Guide](load-balancer-observability-dashboard/docs/dashboard_guide.md)** - Power BI integration
- **[API Documentation](load-balancer-retry-prediction/docs/api_documentation.md)** - ML prediction API

## 🔒 Security

This project implements enterprise-grade security practices:
- No sensitive credentials in source code
- Environment variable-based configuration
- Secure database connection patterns
- Comprehensive `.gitignore` for sensitive files

## 🛠️ Requirements

- **Python 3.8+**
- **SQL Server** (Express or higher)
- **ODBC Driver 17 for SQL Server**
- **Power BI Desktop** (optional, for dashboards)

## 🤝 Contributing

1. Fork the repository
2. Create a feature branch
3. Run the integration tests
4. Submit a pull request

## 📧 Contact

**Author:** Fares Chehidi  
**Email:** fareschehidi28@gmail.com  
**GitHub:** [@FCHEHIDI](https://github.com/FCHEHIDI)

## 📜 License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

---

⭐ **Star this repository** if you find it useful for your load balancer analytics needs!
