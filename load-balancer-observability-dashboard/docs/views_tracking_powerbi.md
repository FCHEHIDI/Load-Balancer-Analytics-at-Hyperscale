# Power BI Data Sources and Views Reference - TrafficInsights Golden Layer

**Author**: Fares Chehidi (fareschehidi@gmail.com)  
**Version**: 2.0.0 - Updated for TrafficInsights Golden Layer  
**Created**: 2025-07-09

## Overview

This document provides a comprehensive reference for all SQL tables, views, and data sources used in the Load Balancer Observability Power BI dashboard. The system now uses the **TrafficInsights** database with a golden layer architecture that provides advanced analytics views for comprehensive load balancer monitoring.

## Database: TrafficInsights

The TrafficInsights database serves as our golden layer, providing curated, analytics-ready views for Power BI consumption.

## Core Data Tables

### Primary Tables

| Table Name | Purpose | Key Columns | Power BI Usage |
|------------|---------|-------------|----------------|
| `RequestLogs` | Individual request telemetry | timestamp, server_id, status_code, response_time_ms, retry_rate | Main fact table for request analytics |
| `ServerMetrics` | Server performance data | timestamp, server_id, cpu_usage_percent, memory_usage_percent | Infrastructure monitoring visuals |
| `AnalyticsReports` | Computed KPI reports | report_timestamp, report_type, report_data | Pre-aggregated dashboard metrics |

## Golden Layer Views (Primary Power BI Data Sources)

### 1. Request KPIs (`vw_RequestKPIs`)
**Purpose**: Primary performance indicators and metrics
```sql
-- Core KPIs with calculated metrics
SELECT 
    total_requests,
    requests_per_second,
    avg_response_time_ms,
    p95_response_time_ms,
    error_rate_percent,
    avg_retry_rate
FROM vw_RequestKPIs
```

**Power BI Usage**: 
- Main KPI cards on executive dashboard
- Performance trend analysis
- SLA compliance monitoring

### 2. Server Health (`vw_ServerHealth`)
**Purpose**: Infrastructure monitoring and capacity planning
```sql
-- Server performance aggregations
SELECT 
    server_id,
    avg_cpu,
    avg_memory,
    avg_disk,
    avg_rps,
    total_failures,
    metric_snapshots
FROM vw_ServerHealth
```

**Power BI Usage**:
- Server health matrix visualization
- Resource utilization dashboards
- Capacity planning analytics

### 3. Traffic Patterns (`vw_TrafficPatterns`)
**Purpose**: Temporal traffic analysis and pattern recognition
```sql
-- Time-based traffic analysis
SELECT 
    hour_of_day,
    weekday,
    request_volume,
    avg_latency
FROM vw_TrafficPatterns
```

**Power BI Usage**:
- Traffic volume heatmaps
- Peak hour analysis
- Weekly/daily pattern identification

### 4. Anomaly Flags (`vw_AnomalyFlags`) ⭐ **Advanced Analytics**
**Purpose**: Comprehensive anomaly detection with severity classification
```sql
-- Advanced anomaly detection with rich metadata
SELECT 
    request_id,
    server_id,
    region,
    request_timestamp,
    request_method,
    status_code,
    response_time_ms,
    retry_rate,
    
    -- Time granularity
    RequestHour,
    RequestMinute,
    TimeBucket,
    
    -- Behavioral flags
    IsFailure,
    IsLatencyOutlier,
    IsRetrySpike,
    
    -- Scoring and classification
    AnomalyScore,
    SeverityTier,
    FailureType,
    LatencyBucket,
    MethodCategory,
    MethodDisplay,
    
    -- Temporal context
    DayName,
    IsWeekend
FROM vw_AnomalyFlags
```

**Power BI Usage**:
- Anomaly detection dashboards
- Severity timeline visualization
- Root cause analysis
- Alert management
- Pattern correlation analysis

### 5. Latest Analytics Reports (`vw_LatestAnalyticsReports`)
**Purpose**: Most recent analytics reports and insights
```sql
-- Recent analytics reports
SELECT TOP 10
    report_timestamp,
    report_type,
    report_data,
    created_at
FROM vw_LatestAnalyticsReports
ORDER BY created_at DESC
```

**Power BI Usage**:
- Recent insights panel
- Analytics report history
- Data quality monitoring

## Power BI Dashboard Integration

### Dashboard Architecture

#### Page 1: Executive Overview
- **Primary Data Source**: `vw_RequestKPIs`
- **Supporting Sources**: `vw_TrafficPatterns`
- **Key Visuals**: KPI cards, trend lines, executive summary
- **Refresh Rate**: Every 5 minutes

#### Page 2: Infrastructure Health
- **Primary Data Source**: `vw_ServerHealth`
- **Supporting Sources**: `ServerMetrics`
- **Key Visuals**: Server health matrix, resource utilization
- **Refresh Rate**: Every 2 minutes

#### Page 3: Anomaly Detection 🎯
- **Primary Data Source**: `vw_AnomalyFlags`
- **Key Visuals**: 
  - Severity timeline
  - Anomaly score distribution
  - Failure type analysis
  - Method category breakdown
  - Latency bucket distribution
- **Refresh Rate**: Every 1 minute

#### Page 4: Traffic Analytics
- **Primary Data Source**: `vw_TrafficPatterns`
- **Key Visuals**: Traffic heatmaps, volume trends, pattern analysis
- **Refresh Rate**: Every 10 minutes

## Advanced Analytics Queries

### Anomaly Correlation Analysis
```sql
-- Cross-reference anomalies with server health
SELECT 
    af.SeverityTier,
    af.server_id,
    sh.avg_cpu,
    sh.avg_memory,
    COUNT(*) as anomaly_count
FROM vw_AnomalyFlags af
JOIN vw_ServerHealth sh ON af.server_id = sh.server_id
WHERE af.AnomalyScore > 0
GROUP BY af.SeverityTier, af.server_id, sh.avg_cpu, sh.avg_memory
```

### Peak Hour Performance Analysis
```sql
-- Performance during peak traffic hours
SELECT 
    tp.hour_of_day,
    rk.avg_response_time_ms,
    rk.error_rate_percent,
    tp.request_volume
FROM vw_TrafficPatterns tp
CROSS JOIN vw_RequestKPIs rk
WHERE tp.request_volume > (SELECT AVG(request_volume) * 1.5 FROM vw_TrafficPatterns)
```

### Critical Anomaly Timeline
```sql
-- Timeline of critical anomalies with context
SELECT 
    request_timestamp,
    server_id,
    FailureType,
    LatencyBucket,
    MethodDisplay,
    AnomalyScore
FROM vw_AnomalyFlags
WHERE SeverityTier = 'Critical'
ORDER BY request_timestamp DESC
```

## Data Connection Configuration

### TrafficInsights Connection String
```text
Server: [Your SQL Server Instance]
Database: TrafficInsights
Authentication: Windows Integrated / SQL Server
Timeout Settings: 
  - Connection: 30 seconds
  - Command: 300 seconds
```

### Recommended Refresh Schedule
```json
{
  "refreshSchedule": {
    "goldenLayerViews": {
      "vw_RequestKPIs": "5 minutes",
      "vw_ServerHealth": "2 minutes",
      "vw_AnomalyFlags": "1 minute",
      "vw_TrafficPatterns": "10 minutes",
      "vw_LatestAnalyticsReports": "15 minutes"
    },
    "rawTables": {
      "RequestLogs": "1 hour",
      "ServerMetrics": "30 minutes"
    }
  }
}
```

## Key Features of Golden Layer

### 🎯 **Advanced Anomaly Detection**
- Multi-dimensional anomaly scoring
- Severity classification (Critical, Moderate, Minor, Normal)
- Rich contextual metadata for root cause analysis

### 📊 **Performance Analytics**
- Real-time KPI calculations
- Percentile-based performance metrics
- Traffic pattern recognition

### 🔍 **Enhanced Categorization**
- Emoji-enhanced method displays
- Latency bucket classifications
- Failure type categorization
- Weekend/weekday analysis

### ⚡ **Optimized for Power BI**
- Pre-aggregated metrics for fast dashboard loading
- Rich categorical data for advanced filtering
- Time-based granularity for temporal analysis

### Custom Power BI Queries

#### Request Volume Analysis
```sql
SELECT 
    DATEPART(HOUR, timestamp) as hour_of_day,
    region,
    COUNT(*) as request_count,
    AVG(response_time_ms) as avg_response_time
FROM RequestLogs
WHERE timestamp >= DATEADD(DAY, -7, GETDATE())
GROUP BY DATEPART(HOUR, timestamp), region
ORDER BY hour_of_day, region
```

#### Error Rate Trending
```sql
SELECT 
    CAST(timestamp AS DATE) as date,
    server_id,
    SUM(CASE WHEN status_code >= 400 THEN 1 ELSE 0 END) * 100.0 / COUNT(*) as error_rate
FROM RequestLogs
WHERE timestamp >= DATEADD(DAY, -30, GETDATE())
GROUP BY CAST(timestamp AS DATE), server_id
ORDER BY date, server_id
```

#### Retry Pattern Analysis
```sql
SELECT 
    CASE 
        WHEN retry_rate = 0 THEN 'No Retries'
        WHEN retry_rate <= 0.1 THEN 'Low Retry (≤10%)'
        WHEN retry_rate <= 0.3 THEN 'Medium Retry (11-30%)'
        ELSE 'High Retry (>30%)'
    END as retry_category,
    AVG(response_time_ms) as avg_response_time,
    COUNT(*) as request_count
FROM RequestLogs
WHERE timestamp >= DATEADD(DAY, -1, GETDATE())
GROUP BY 
    CASE 
        WHEN retry_rate = 0 THEN 'No Retries'
        WHEN retry_rate <= 0.1 THEN 'Low Retry (≤10%)'
        WHEN retry_rate <= 0.3 THEN 'Medium Retry (11-30%)'
        ELSE 'High Retry (>30%)'
    END
```

## Power BI Dashboard Structure

### Page 1: Executive Overview
- **Data Sources**: `vw_RealTimeKPIs`, `RequestLogs`
- **Key Visuals**: KPI cards, trend lines, summary statistics
- **Refresh Rate**: Every 5 minutes

### Page 2: Infrastructure Health
- **Data Sources**: `vw_ServerHealthSummary`, `ServerMetrics`
- **Key Visuals**: Server matrix, resource utilization charts
- **Refresh Rate**: Every 2 minutes

### Page 3: Performance Analytics
- **Data Sources**: `RequestLogs`, `PerformanceBaselines`
- **Key Visuals**: Response time distribution, percentile analysis
- **Refresh Rate**: Every 10 minutes

### Page 4: Alert Management
- **Data Sources**: `AlertHistory`, `AlertDefinitions`
- **Key Visuals**: Alert timeline, severity distribution
- **Refresh Rate**: Every 1 minute

## Data Refresh Configuration

### Automatic Refresh Settings
```json
{
  "refreshSchedule": {
    "realTimeKPIs": "5 minutes",
    "serverHealth": "2 minutes", 
    "performanceMetrics": "10 minutes",
    "alertData": "1 minute",
    "historicalData": "1 hour"
  }
}
```

### Data Source Connection Strings
```text
Server Connection: [Configured in Power BI Service]
Database: LoadBalancerObservability
Authentication: Windows Integrated / SQL Server
Connection Timeout: 30 seconds
Command Timeout: 300 seconds
```

## Performance Optimization

### Recommended Indexes
The following indexes are automatically created by the database schema:
- `IX_RequestLogs_Timestamp` - For time-based filtering
- `IX_RequestLogs_Server` - For server-based grouping
- `IX_ServerMetrics_Performance` - For resource utilization queries

### Query Performance Tips
1. Always filter by timestamp for large table queries
2. Use pre-aggregated views when possible
3. Limit date ranges to necessary periods
4. Use server_id indexing for server-specific analysis

## Troubleshooting

### Common Issues
1. **Slow Dashboard Load**: Check index usage and query execution plans
2. **Data Freshness**: Verify database connectivity and refresh schedules
3. **Missing Data**: Check data generation pipeline and ETL processes

### Performance Monitoring
Monitor these metrics for optimal Power BI performance:
- Query execution time < 30 seconds
- Data refresh completion < 5 minutes
- Dashboard load time < 10 seconds

## Change Log

| Date | Version | Changes |
|------|---------|---------|
| 2025-07-09 | 1.0.0 | Initial documentation with core views and tables |

## See Also

- [Database Schema Documentation](../config/database_schema.sql)
- [Dashboard User Guide](dashboard_guide.md)
- [Architecture Overview](architecture_overview.md)
- [Analytics Methodology](modeling_rationale.md)

---

*This documentation is maintained alongside the Power BI dashboard development and should be updated when new data sources or views are added.*
