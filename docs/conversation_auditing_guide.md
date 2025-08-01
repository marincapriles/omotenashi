# Conversation Auditing System

This document explains how to use the comprehensive conversation auditing system for the Omotenashi Telegram bot.

## Overview

The auditing system automatically logs all Telegram conversations with detailed information including:

- Complete conversation history (user messages and agent responses)
- Detailed agent reasoning for each response
- Tool usage with execution times and reasoning
- Error tracking and rate limiting incidents
- Session context and user information
- Performance metrics

## Database Schema

The system uses SQLite database with two main tables:

### `conversations` table
- Complete conversation records with user info, messages, reasoning
- Processing time, error status, session context
- JSON field for tool usage summary

### `tool_usage` table  
- Detailed tool execution records
- Input parameters, output, execution time
- Success/failure status and reasoning

## Automatic Logging

All conversations are automatically logged when users interact with the Telegram bot. No configuration required - logging happens transparently in the background.

### What Gets Logged

**For Each Message Exchange:**
- User information (ID, username, first/last name)
- Complete message text (user input and agent response)
- Agent's reasoning process
- All tools used with detailed context
- Processing time and performance metrics
- Error details if any issues occurred
- Rate limiting incidents

**Tool Usage Details:**
- Tool name and input parameters
- Generated output
- Execution time in milliseconds
- Success/failure status
- Reasoning for why tool was selected and used

## Accessing Audit Data

### 1. Command Line Reports

Use the audit report generator script:

```bash
# Show usage statistics for last 7 days
python scripts/generate_audit_report.py stats --days 7

# Generate daily HTML report
python scripts/generate_audit_report.py daily

# Generate weekly HTML report  
python scripts/generate_audit_report.py weekly

# Export conversations to CSV
python scripts/generate_audit_report.py export --days 30

# Show recent conversations
python scripts/generate_audit_report.py recent --limit 20

# Filter by specific user
python scripts/generate_audit_report.py stats --user-id 123456789
```

### 2. HTML Reports

Generated reports include:
- Usage statistics and performance metrics
- Tool usage analysis
- Error rate and rate limiting incidents
- Recommendations for optimization

### 3. CSV Export

Export conversation data for analysis in Excel or other tools:
- All conversation details
- Tool usage summary
- Performance metrics
- Filterable by user or date range

### 4. Direct Database Access

The SQLite database is located at: `logs/conversations.db`

You can query it directly:

```sql
-- Show conversations from last 24 hours
SELECT timestamp, first_name, user_message, agent_response 
FROM conversations 
WHERE datetime(timestamp) > datetime('now', '-1 day');

-- Tool usage statistics
SELECT tool_name, COUNT(*) as usage_count, AVG(execution_time_ms) as avg_time
FROM tool_usage 
GROUP BY tool_name 
ORDER BY usage_count DESC;

-- Error analysis
SELECT error_details, COUNT(*) as frequency
FROM conversations 
WHERE error_occurred = 1 
GROUP BY error_details;
```

## Privacy and Security

- Database contains conversation content - ensure proper access controls
- User IDs and names are stored - comply with privacy regulations
- Consider data retention policies for long-term storage
- Database file should be backed up regularly

## Monitoring and Alerts

### Key Metrics to Monitor

1. **Error Rate** - Should be < 5%
2. **Processing Time** - Should be < 3000ms average
3. **Rate Limiting** - Should be < 10% of conversations
4. **Tool Performance** - Monitor slow-running tools

### Setting Up Alerts

Create monitoring scripts that check these metrics and alert when thresholds are exceeded:

```bash
# Example: Check error rate and alert if > 5%
python scripts/generate_audit_report.py stats --days 1 | grep "Error Rate"
```

## Maintenance

### Database Cleanup

Periodically clean old records to manage database size:

```python
from src.omotenashi.conversation_logger import get_conversation_logger
import sqlite3
from datetime import datetime, timedelta

# Remove records older than 90 days
logger = get_conversation_logger()
cutoff_date = (datetime.now() - timedelta(days=90)).isoformat()

with sqlite3.connect(logger.db_path) as conn:
    conn.execute("DELETE FROM tool_usage WHERE timestamp < ?", (cutoff_date,))
    conn.execute("DELETE FROM conversations WHERE timestamp < ?", (cutoff_date,))
    conn.commit()
```

### Performance Optimization

For high-volume usage:
- Consider moving to PostgreSQL for better performance
- Implement database partitioning by date
- Add more indexes for common queries
- Use connection pooling

## Troubleshooting

### Common Issues

**Database locked errors:**
- Multiple processes accessing database simultaneously
- Use connection pooling or implement retry logic

**Missing conversation logs:**
- Check file permissions on logs directory
- Verify database initialization completed successfully
- Check for exceptions in Telegram bot logs

**Performance issues:**
- Database size growing too large - implement cleanup
- Complex queries taking too long - add indexes
- High volume logging - consider async logging

### Debug Mode

Enable detailed logging in the Telegram bot:

```python
# In telegram_bot.py
logging.getLogger().setLevel(logging.DEBUG)
```

## Example Queries

### Most Active Users
```sql
SELECT user_id, first_name, COUNT(*) as message_count
FROM conversations 
WHERE timestamp > datetime('now', '-7 days')
GROUP BY user_id 
ORDER BY message_count DESC 
LIMIT 10;
```

### Tool Performance Analysis
```sql
SELECT 
    tool_name,
    COUNT(*) as usage_count,
    AVG(execution_time_ms) as avg_time,
    MIN(execution_time_ms) as min_time,
    MAX(execution_time_ms) as max_time,
    SUM(CASE WHEN success = 0 THEN 1 ELSE 0 END) as error_count
FROM tool_usage 
WHERE timestamp > datetime('now', '-7 days')
GROUP BY tool_name 
ORDER BY usage_count DESC;
```

### Conversation Flow Analysis
```sql
SELECT 
    session_message_count,
    COUNT(*) as conversations,
    AVG(processing_time_ms) as avg_processing_time
FROM conversations 
GROUP BY session_message_count 
ORDER BY session_message_count;
```

This auditing system provides comprehensive visibility into how users interact with the Omotenashi concierge and helps identify areas for improvement.