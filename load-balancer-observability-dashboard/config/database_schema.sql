-- Load Balancer Observability Database Schema
-- Author: Fares Chehidi (fareschehidi@gmail.com)
-- Version: 2.0.0 - Updated with TrafficInsights Golden Layer
-- Created: 2025-07-09

-- Create database if it doesn't exist
USE master;
GO

IF NOT EXISTS (SELECT name FROM sys.databases WHERE name = 'TrafficInsights')
BEGIN
    CREATE DATABASE TrafficInsights;
END
GO

USE TrafficInsights;
GO

-- Request Logs Table
-- Stores individual request telemetry data
IF OBJECT_ID('RequestLogs') IS NULL
BEGIN
    CREATE TABLE [dbo].[RequestLogs](
        [id] [bigint] IDENTITY(1,1) NOT NULL,
        [timestamp] [datetime2](7) NULL,
        [server_id] [varchar](50) NULL,
        [region] [varchar](50) NULL,
        [request_method] [varchar](10) NULL,
        [status_code] [int] NULL,
        [response_time_ms] [int] NULL,
        [retry_rate] [float] NULL,
        [bytes_sent] [bigint] NULL,
        [client_ip] [varchar](45) NULL,
        [user_agent] [varchar](255) NULL,
        [created_at] [datetime2](7) NULL,
    PRIMARY KEY CLUSTERED 
    (
        [id] ASC
    )WITH (PAD_INDEX = OFF, STATISTICS_NORECOMPUTE = OFF, IGNORE_DUP_KEY = OFF, ALLOW_ROW_LOCKS = ON, ALLOW_PAGE_LOCKS = ON, OPTIMIZE_FOR_SEQUENTIAL_KEY = OFF) ON [PRIMARY]
    ) ON [PRIMARY];
    
    -- Add default constraint
    ALTER TABLE [dbo].[RequestLogs] ADD DEFAULT (getdate()) FOR [created_at];
    
    PRINT 'RequestLogs table created successfully';
END
GO

-- Server Metrics Table
-- Stores server performance and health metrics
IF OBJECT_ID('ServerMetrics') IS NULL
BEGIN
    CREATE TABLE [dbo].[ServerMetrics](
        [id] [bigint] IDENTITY(1,1) NOT NULL,
        [timestamp] [datetime2](7) NULL,
        [server_id] [varchar](50) NULL,
        [cpu_usage_percent] [float] NULL,
        [memory_usage_percent] [float] NULL,
        [disk_usage_percent] [float] NULL,
        [network_in_mbps] [float] NULL,
        [network_out_mbps] [float] NULL,
        [active_connections] [int] NULL,
        [requests_per_second] [int] NULL,
        [backend_health_failures] [int] NULL,
        [created_at] [datetime2](7) NULL,
    PRIMARY KEY CLUSTERED 
    (
        [id] ASC
    )WITH (PAD_INDEX = OFF, STATISTICS_NORECOMPUTE = OFF, IGNORE_DUP_KEY = OFF, ALLOW_ROW_LOCKS = ON, ALLOW_PAGE_LOCKS = ON, OPTIMIZE_FOR_SEQUENTIAL_KEY = OFF) ON [PRIMARY]
    ) ON [PRIMARY];
    
    -- Add default constraint
    ALTER TABLE [dbo].[ServerMetrics] ADD DEFAULT (getdate()) FOR [created_at];
    
    PRINT 'ServerMetrics table created successfully';
END
GO

-- Analytics Reports Table
-- Stores computed analytics reports and KPIs
IF OBJECT_ID('AnalyticsReports') IS NULL
BEGIN
    CREATE TABLE [dbo].[AnalyticsReports](
        [id] [bigint] IDENTITY(1,1) NOT NULL,
        [report_timestamp] [datetime2](7) NULL,
        [report_type] [varchar](50) NULL,
        [report_data] [nvarchar](max) NULL,
        [created_at] [datetime2](7) NULL,
    PRIMARY KEY CLUSTERED 
    (
        [id] ASC
    )WITH (PAD_INDEX = OFF, STATISTICS_NORECOMPUTE = OFF, IGNORE_DUP_KEY = OFF, ALLOW_ROW_LOCKS = ON, ALLOW_PAGE_LOCKS = ON, OPTIMIZE_FOR_SEQUENTIAL_KEY = OFF) ON [PRIMARY]
    ) ON [PRIMARY] TEXTIMAGE_ON [PRIMARY];
    
    -- Add default constraint
    ALTER TABLE [dbo].[AnalyticsReports] ADD DEFAULT (getdate()) FOR [created_at];
    
    PRINT 'AnalyticsReports table created successfully';
END
GO

-- TrafficInsights Golden Layer Views
-- These views provide the core analytics layer for Power BI dashboards

-- Request KPIs View - Primary performance indicators
IF OBJECT_ID('vw_RequestKPIs') IS NULL
BEGIN
    EXEC('
    CREATE VIEW [dbo].[vw_RequestKPIs] AS
    WITH RequestStats AS (
        SELECT
            COUNT(*) AS total_requests,
            ROUND(COUNT(*) * 1.0 / NULLIF(DATEDIFF(SECOND, MIN(timestamp), MAX(timestamp)), 0), 2) AS requests_per_second,
            ROUND(AVG(response_time_ms), 2) AS avg_response_time_ms,
            ROUND(SUM(CASE WHEN status_code >= 400 THEN 1 ELSE 0 END) * 100.0 / COUNT(*), 2) AS error_rate_percent,
            ROUND(AVG(retry_rate), 3) AS avg_retry_rate
        FROM RequestLogs
    ),
    Percentiles AS (
        SELECT
            ROUND(PERCENTILE_CONT(0.95) WITHIN GROUP (ORDER BY response_time_ms) OVER (), 2) AS p95_response_time_ms
        FROM RequestLogs
    )
    SELECT
        rs.total_requests,
        rs.requests_per_second,
        rs.avg_response_time_ms,
        p.p95_response_time_ms,
        rs.error_rate_percent,
        rs.avg_retry_rate
    FROM RequestStats rs
    CROSS JOIN (SELECT TOP 1 * FROM Percentiles) p
    ');
    
    PRINT 'vw_RequestKPIs view created successfully';
END
GO

-- Server Health View - Infrastructure monitoring
IF OBJECT_ID('vw_ServerHealth') IS NULL
BEGIN
    EXEC('
    CREATE VIEW [dbo].[vw_ServerHealth] AS
    SELECT
        server_id,
        ROUND(AVG(cpu_usage_percent), 2) AS avg_cpu,
        ROUND(AVG(memory_usage_percent), 2) AS avg_memory,
        ROUND(AVG(disk_usage_percent), 2) AS avg_disk,
        ROUND(AVG(requests_per_second), 2) AS avg_rps,
        SUM(backend_health_failures) AS total_failures,
        COUNT(*) AS metric_snapshots
    FROM ServerMetrics
    GROUP BY server_id
    ');
    
    PRINT 'vw_ServerHealth view created successfully';
END
GO

-- Traffic Patterns View - Temporal analysis
IF OBJECT_ID('vw_TrafficPatterns') IS NULL
BEGIN
    EXEC('
    CREATE VIEW [dbo].[vw_TrafficPatterns] AS
    SELECT
        DATEPART(HOUR, timestamp) AS hour_of_day,
        DATENAME(WEEKDAY, timestamp) AS weekday,
        COUNT(*) AS request_volume,
        ROUND(AVG(response_time_ms), 2) AS avg_latency
    FROM RequestLogs
    GROUP BY DATEPART(HOUR, timestamp), DATENAME(WEEKDAY, timestamp)
    ');
    
    PRINT 'vw_TrafficPatterns view created successfully';
END
GO

-- Anomaly Flags View - Advanced anomaly detection with severity classification
IF OBJECT_ID('vw_AnomalyFlags') IS NULL
BEGIN
    EXEC('
    CREATE VIEW [dbo].[vw_AnomalyFlags] AS
    SELECT
        -- Core identifiers
        id AS request_id,
        server_id,
        region,
        timestamp AS request_timestamp,
        request_method,
        status_code,
        response_time_ms,
        retry_rate,
        bytes_sent,
        client_ip,
        user_agent,

        -- Time granularity
        DATEPART(HOUR, timestamp) AS RequestHour,
        DATEPART(MINUTE, timestamp) AS RequestMinute,
        DATEPART(SECOND, timestamp) AS RequestSecond,
        FORMAT(timestamp, ''HH:mm:ss'') AS TimeBucket,

        -- Behavioral flags
        CASE WHEN status_code IN (500, 503, 504) THEN 1 ELSE 0 END AS IsFailure,
        CASE WHEN response_time_ms > 1000 THEN 1 ELSE 0 END AS IsLatencyOutlier,
        CASE WHEN retry_rate > 0.3 THEN 1 ELSE 0 END AS IsRetrySpike,

        -- Composite anomaly score
        (
            CASE WHEN retry_rate > 0.3 THEN 1 ELSE 0 END +
            CASE WHEN response_time_ms > 1000 THEN 1 ELSE 0 END +
            CASE WHEN status_code IN (500, 503, 504) THEN 1 ELSE 0 END
        ) AS AnomalyScore,

        -- Severity tiering
        CASE
            WHEN (
                CASE WHEN retry_rate > 0.3 THEN 1 ELSE 0 END +
                CASE WHEN response_time_ms > 1000 THEN 1 ELSE 0 END +
                CASE WHEN status_code IN (500, 503, 504) THEN 1 ELSE 0 END
            ) = 3 THEN ''Critical''
            WHEN (
                CASE WHEN retry_rate > 0.3 THEN 1 ELSE 0 END +
                CASE WHEN response_time_ms > 1000 THEN 1 ELSE 0 END +
                CASE WHEN status_code IN (500, 503, 504) THEN 1 ELSE 0 END
            ) = 2 THEN ''Moderate''
            WHEN (
                CASE WHEN retry_rate > 0.3 THEN 1 ELSE 0 END +
                CASE WHEN response_time_ms > 1000 THEN 1 ELSE 0 END +
                CASE WHEN status_code IN (500, 503, 504) THEN 1 ELSE 0 END
            ) = 1 THEN ''Minor''
            ELSE ''Normal''
        END AS SeverityTier,

        -- Failure category
        CASE 
            WHEN status_code = 500 THEN ''Internal Error''
            WHEN status_code = 503 THEN ''Service Unavailable''
            WHEN status_code = 504 THEN ''Gateway Timeout''
            ELSE ''Other''
        END AS FailureType,

        -- Latency bucket
        CASE 
            WHEN response_time_ms <= 500 THEN ''Fast''
            WHEN response_time_ms <= 1000 THEN ''Moderate''
            WHEN response_time_ms <= 3000 THEN ''Slow''
            ELSE ''Very Slow''
        END AS LatencyBucket,

        -- Method category
        CASE 
            WHEN request_method IN (''GET'', ''HEAD'') THEN ''Read''
            WHEN request_method IN (''POST'', ''PUT'', ''PATCH'') THEN ''Write''
            WHEN request_method = ''DELETE'' THEN ''Danger Zone''
            ELSE ''Other''
        END AS MethodCategory,

        -- Emoji-labeled request methods
        CASE 
            WHEN request_method = ''GET'' THEN ''GET 🔍''
            WHEN request_method = ''POST'' THEN ''POST 📨''
            WHEN request_method = ''PUT'' THEN ''PUT 🛠️''
            WHEN request_method = ''DELETE'' THEN ''DELETE ⚠️''
            ELSE CONCAT(request_method, '' ❓'')
        END AS MethodDisplay,

        -- Day tagging
        DATENAME(WEEKDAY, timestamp) AS DayName,
        CASE WHEN DATEPART(WEEKDAY, timestamp) IN (1,7) THEN 1 ELSE 0 END AS IsWeekend

    FROM dbo.RequestLogs
    ');
    
    PRINT 'vw_AnomalyFlags view created successfully';
END
GO

-- Latest Analytics Reports View - Most recent reports
IF OBJECT_ID('vw_LatestAnalyticsReports') IS NULL
BEGIN
    EXEC('
    CREATE VIEW [dbo].[vw_LatestAnalyticsReports] AS
    SELECT TOP 10
        report_timestamp,
        report_type,
        report_data,
        created_at
    FROM AnalyticsReports
    ORDER BY created_at DESC
    ');
    
    PRINT 'vw_LatestAnalyticsReports view created successfully';
END
GO

-- Legacy compatibility views (mapping old view names to new structure)
-- Real-time KPIs View (legacy compatibility)
IF OBJECT_ID('vw_RealTimeKPIs') IS NULL
BEGIN
    EXEC('
    CREATE VIEW vw_RealTimeKPIs AS
    SELECT 
        DATEADD(MINUTE, DATEDIFF(MINUTE, 0, GETDATE()) / 5 * 5, 0) as time_bucket,
        total_requests,
        avg_response_time_ms as avg_response_time,
        p95_response_time_ms as p95_response_time,
        p95_response_time_ms as p99_response_time,
        error_rate_percent,
        avg_retry_rate
    FROM vw_RequestKPIs
    ');
    
    PRINT 'vw_RealTimeKPIs (legacy compatibility) view created successfully';
END
GO

-- Server Health Summary View (legacy compatibility)
IF OBJECT_ID('vw_ServerHealthSummary') IS NULL
BEGIN
    EXEC('
    CREATE VIEW vw_ServerHealthSummary AS
    SELECT 
        server_id,
        avg_cpu as avg_cpu_usage,
        avg_memory as avg_memory_usage,
        avg_rps as avg_connections,
        total_failures as total_health_failures,
        GETDATE() as last_update
    FROM vw_ServerHealth
    ');
    
    PRINT 'vw_ServerHealthSummary (legacy compatibility) view created successfully';
END
GO

-- Create stored procedures for common operations
-- Data cleanup procedure
IF OBJECT_ID('sp_CleanupOldData') IS NULL
BEGIN
    EXEC('
    CREATE PROCEDURE sp_CleanupOldData
        @RetentionDays INT = 90
    AS
    BEGIN
        SET NOCOUNT ON;
        
        DECLARE @CutoffDate DATETIME2 = DATEADD(DAY, -@RetentionDays, GETDATE());
        DECLARE @DeletedRows INT = 0;
        
        -- Clean RequestLogs
        DELETE FROM RequestLogs WHERE created_at < @CutoffDate;
        SET @DeletedRows = @@ROWCOUNT;
        PRINT ''Deleted '' + CAST(@DeletedRows AS VARCHAR(10)) + '' records from RequestLogs'';
        
        -- Clean ServerMetrics
        DELETE FROM ServerMetrics WHERE created_at < @CutoffDate;
        SET @DeletedRows = @@ROWCOUNT;
        PRINT ''Deleted '' + CAST(@DeletedRows AS VARCHAR(10)) + '' records from ServerMetrics'';
        
        -- Clean AnalyticsReports (keep longer retention)
        DELETE FROM AnalyticsReports WHERE created_at < DATEADD(DAY, -@RetentionDays * 2, GETDATE());
        SET @DeletedRows = @@ROWCOUNT;
        PRINT ''Deleted '' + CAST(@DeletedRows AS VARCHAR(10)) + '' records from AnalyticsReports'';
    END
    ');
    
    PRINT 'sp_CleanupOldData procedure created successfully';
END
GO

-- Data quality check procedure
IF OBJECT_ID('sp_CheckDataQuality') IS NULL
BEGIN
    EXEC('
    CREATE PROCEDURE sp_CheckDataQuality
    AS
    BEGIN
        SET NOCOUNT ON;
        
        DECLARE @RequestLogsCount INT;
        DECLARE @ServerMetricsCount INT;
        DECLARE @QualityScore FLOAT;
        
        SELECT @RequestLogsCount = COUNT(*) FROM RequestLogs WHERE created_at >= DATEADD(HOUR, -1, GETDATE());
        SELECT @ServerMetricsCount = COUNT(*) FROM ServerMetrics WHERE created_at >= DATEADD(HOUR, -1, GETDATE());
        
        SET @QualityScore = CASE 
            WHEN @RequestLogsCount > 0 AND @ServerMetricsCount > 0 THEN 95.0
            WHEN @RequestLogsCount > 0 OR @ServerMetricsCount > 0 THEN 75.0
            ELSE 25.0
        END;
        
        PRINT ''Data Quality Check Completed'';
        PRINT ''Request Logs (last hour): '' + CAST(@RequestLogsCount AS VARCHAR(10));
        PRINT ''Server Metrics (last hour): '' + CAST(@ServerMetricsCount AS VARCHAR(10));
        PRINT ''Quality Score: '' + CAST(@QualityScore AS VARCHAR(10)) + ''%'';
    END
    ');
    
    PRINT 'sp_CheckDataQuality procedure created successfully';
END
GO

-- Grant permissions for application user
-- Note: In production, create specific user accounts with minimal required permissions
PRINT 'TrafficInsights Database Schema Setup Completed Successfully!';
PRINT '';
PRINT 'TABLES CREATED:';
PRINT '- RequestLogs: Individual request telemetry data';
PRINT '- ServerMetrics: Server performance and health metrics';
PRINT '- AnalyticsReports: Computed analytics reports and KPIs';
PRINT '';
PRINT 'GOLDEN LAYER VIEWS CREATED:';
PRINT '- vw_RequestKPIs: Primary performance indicators';
PRINT '- vw_ServerHealth: Infrastructure monitoring metrics';
PRINT '- vw_TrafficPatterns: Temporal traffic analysis';
PRINT '- vw_AnomalyFlags: Advanced anomaly detection with severity classification';
PRINT '- vw_LatestAnalyticsReports: Most recent analytics reports';
PRINT '';
PRINT 'LEGACY COMPATIBILITY VIEWS:';
PRINT '- vw_RealTimeKPIs: Legacy compatibility for existing dashboards';
PRINT '- vw_ServerHealthSummary: Legacy compatibility for server health monitoring';
PRINT '';
PRINT 'PROCEDURES CREATED:';
PRINT '- sp_CleanupOldData: Automated data retention management';
PRINT '- sp_CheckDataQuality: Data quality monitoring and validation';
PRINT '';
PRINT 'NEXT STEPS:';
PRINT '1. Update application connection strings to use TrafficInsights database';
PRINT '2. Configure Power BI dashboards to use golden layer views';
PRINT '3. Set up automated cleanup job for sp_CleanupOldData';
PRINT '4. Configure monitoring for data quality checks';
PRINT '5. Import initial test data using the data generation scripts';
PRINT '';
PRINT 'POWER BI INTEGRATION:';
PRINT '- Primary views: vw_RequestKPIs, vw_ServerHealth, vw_TrafficPatterns, vw_AnomalyFlags';
PRINT '- See docs/views_tracking_powerbi.md for detailed Power BI integration guide';
GO
