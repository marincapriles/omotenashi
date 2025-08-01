"""
Conversation Logger for Omotenashi Telegram Bot
----------------------------------------------
This module provides comprehensive logging and auditing capabilities for 
Telegram bot conversations, including detailed reasoning, tool usage, 
and conversation flow tracking.
"""

import json
import sqlite3
import asyncio
import aiosqlite
from datetime import datetime, timedelta
from pathlib import Path
from typing import Dict, List, Any, Optional
from dataclasses import dataclass, asdict
import logging
import concurrent.futures

@dataclass
class ToolUsage:
    """Represents a single tool usage with detailed context."""
    tool_name: str
    input_parameters: Dict[str, Any]
    output: str
    reasoning: str
    execution_time_ms: float
    success: bool
    error_message: Optional[str] = None

@dataclass
class ConversationEntry:
    """Represents a complete conversation exchange."""
    # Identifiers
    conversation_id: str
    message_id: str
    timestamp: datetime
    
    # User context
    user_id: int
    username: Optional[str]
    first_name: Optional[str]
    last_name: Optional[str]
    
    # Message content
    user_message: str
    agent_response: str
    
    # Agent reasoning
    agent_reasoning: str
    tools_used: List[ToolUsage]
    
    # Processing metadata
    processing_time_ms: float
    rate_limited: bool
    error_occurred: bool
    
    # Conversation context
    session_message_count: int
    conversation_length_minutes: float
    
    # Optional fields must come last
    error_details: Optional[str] = None

class ConversationLogger:
    """Handles logging and auditing of Telegram bot conversations."""
    
    def __init__(self, db_path: Optional[str] = None, config=None):
        """
        Initialize the conversation logger.
        
        Args:
            db_path: Path to SQLite database file. If None, uses default location.
            config: Configuration object. If None, loads default configuration.
        """
        # Load configuration
        if config is None:
            from .config_manager import get_logging_config, apply_env_overrides
            self.config = apply_env_overrides(get_logging_config())
        else:
            self.config = config
        
        if db_path is None:
            if hasattr(self.config, 'database') and hasattr(self.config.database, 'path'):
                db_path = self.config.database.path
            else:
                db_path = "logs/conversations.db"
        
        self.db_path = Path(db_path)
        self.db_path.parent.mkdir(parents=True, exist_ok=True)
        
        # Set up logging
        self.logger = logging.getLogger(__name__)
        
        # Initialize database
        self._init_database()
        
        # Set secure file permissions (owner read/write only)
        if self.config.security.enable_file_permissions:
            try:
                import stat
                self.db_path.chmod(stat.S_IRUSR | stat.S_IWUSR)
            except Exception as e:
                self.logger.warning(f"Could not set secure permissions on database: {e}")
    
    def _init_database(self):
        """Initialize the SQLite database with required tables."""
        with sqlite3.connect(self.db_path) as conn:
            conn.execute('''
                CREATE TABLE IF NOT EXISTS conversations (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    conversation_id TEXT NOT NULL,
                    message_id TEXT NOT NULL,
                    timestamp TEXT NOT NULL,
                    
                    -- User information
                    user_id INTEGER NOT NULL,
                    username TEXT,
                    first_name TEXT,
                    last_name TEXT,
                    
                    -- Message content
                    user_message TEXT NOT NULL,
                    agent_response TEXT NOT NULL,
                    
                    -- Agent reasoning
                    agent_reasoning TEXT NOT NULL,
                    
                    -- Processing metadata
                    processing_time_ms REAL NOT NULL,
                    rate_limited BOOLEAN NOT NULL,
                    error_occurred BOOLEAN NOT NULL,
                    error_details TEXT,
                    
                    -- Session context
                    session_message_count INTEGER NOT NULL,
                    conversation_length_minutes REAL NOT NULL,
                    
                    -- JSON fields
                    tools_used_json TEXT NOT NULL,
                    
                    UNIQUE(conversation_id, message_id)
                )
            ''')
            
            conn.execute('''
                CREATE TABLE IF NOT EXISTS tool_usage (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    conversation_id TEXT NOT NULL,
                    message_id TEXT NOT NULL,
                    tool_name TEXT NOT NULL,
                    input_parameters_json TEXT NOT NULL,
                    output TEXT NOT NULL,
                    reasoning TEXT NOT NULL,
                    execution_time_ms REAL NOT NULL,
                    success BOOLEAN NOT NULL,
                    error_message TEXT,
                    timestamp TEXT NOT NULL,
                    
                    FOREIGN KEY (conversation_id, message_id) 
                        REFERENCES conversations (conversation_id, message_id)
                )
            ''')
            
            conn.execute('''
                CREATE INDEX IF NOT EXISTS idx_conversations_user_id 
                ON conversations(user_id)
            ''')
            
            conn.execute('''
                CREATE INDEX IF NOT EXISTS idx_conversations_timestamp 
                ON conversations(timestamp)
            ''')
            
            conn.execute('''
                CREATE INDEX IF NOT EXISTS idx_tool_usage_tool_name 
                ON tool_usage(tool_name)
            ''')
    
    async def log_conversation(self, entry: ConversationEntry):
        """
        Log a complete conversation entry to the database asynchronously.
        
        Args:
            entry: ConversationEntry object with all conversation details
        """
        try:
            async with aiosqlite.connect(self.db_path) as conn:
                # Insert main conversation record
                await conn.execute('''
                    INSERT OR REPLACE INTO conversations (
                        conversation_id, message_id, timestamp,
                        user_id, username, first_name, last_name,
                        user_message, agent_response, agent_reasoning,
                        processing_time_ms, rate_limited, error_occurred, error_details,
                        session_message_count, conversation_length_minutes,
                        tools_used_json
                    ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                ''', (
                    entry.conversation_id,
                    entry.message_id,
                    entry.timestamp.isoformat(),
                    entry.user_id,
                    entry.username,
                    entry.first_name,
                    entry.last_name,
                    entry.user_message,
                    entry.agent_response,
                    entry.agent_reasoning,
                    entry.processing_time_ms,
                    entry.rate_limited,
                    entry.error_occurred,
                    entry.error_details,
                    entry.session_message_count,
                    entry.conversation_length_minutes,
                    json.dumps([asdict(tool) for tool in entry.tools_used])
                ))
                
                # Insert detailed tool usage records
                for tool in entry.tools_used:
                    await conn.execute('''
                        INSERT INTO tool_usage (
                            conversation_id, message_id, tool_name,
                            input_parameters_json, output, reasoning,
                            execution_time_ms, success, error_message, timestamp
                        ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                    ''', (
                        entry.conversation_id,
                        entry.message_id,
                        tool.tool_name,
                        json.dumps(tool.input_parameters),
                        tool.output,
                        tool.reasoning,
                        tool.execution_time_ms,
                        tool.success,
                        tool.error_message,
                        entry.timestamp.isoformat()
                    ))
                
                await conn.commit()
                self.logger.info(f"Logged conversation {entry.conversation_id}:{entry.message_id}")
                
        except Exception as e:
            self.logger.error(f"Failed to log conversation: {e}")
            # Don't raise in async context to avoid blocking the event loop
            
    def log_conversation_sync(self, entry: ConversationEntry):
        """
        Synchronous version of log_conversation for backwards compatibility.
        
        Args:
            entry: ConversationEntry object with all conversation details
        """
        try:
            with sqlite3.connect(self.db_path) as conn:
                # Insert main conversation record
                conn.execute('''
                    INSERT OR REPLACE INTO conversations (
                        conversation_id, message_id, timestamp,
                        user_id, username, first_name, last_name,
                        user_message, agent_response, agent_reasoning,
                        processing_time_ms, rate_limited, error_occurred, error_details,
                        session_message_count, conversation_length_minutes,
                        tools_used_json
                    ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                ''', (
                    entry.conversation_id,
                    entry.message_id,
                    entry.timestamp.isoformat(),
                    entry.user_id,
                    entry.username,
                    entry.first_name,
                    entry.last_name,
                    entry.user_message,
                    entry.agent_response,
                    entry.agent_reasoning,
                    entry.processing_time_ms,
                    entry.rate_limited,
                    entry.error_occurred,
                    entry.error_details,
                    entry.session_message_count,
                    entry.conversation_length_minutes,
                    json.dumps([asdict(tool) for tool in entry.tools_used])
                ))
                
                # Insert detailed tool usage records
                for tool in entry.tools_used:
                    conn.execute('''
                        INSERT INTO tool_usage (
                            conversation_id, message_id, tool_name,
                            input_parameters_json, output, reasoning,
                            execution_time_ms, success, error_message, timestamp
                        ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                    ''', (
                        entry.conversation_id,
                        entry.message_id,
                        tool.tool_name,
                        json.dumps(tool.input_parameters),
                        tool.output,
                        tool.reasoning,
                        tool.execution_time_ms,
                        tool.success,
                        tool.error_message,
                        entry.timestamp.isoformat()
                    ))
                
                conn.commit()
                self.logger.info(f"Logged conversation {entry.conversation_id}:{entry.message_id}")
                
        except Exception as e:
            self.logger.error(f"Failed to log conversation: {e}")
            raise
    
    def get_conversation_history(self, user_id: int, limit: int = 50) -> List[ConversationEntry]:
        """
        Retrieve conversation history for a specific user.
        
        Args:
            user_id: Telegram user ID
            limit: Maximum number of entries to return
            
        Returns:
            List of ConversationEntry objects
        """
        with sqlite3.connect(self.db_path) as conn:
            conn.row_factory = sqlite3.Row
            cursor = conn.execute('''
                SELECT * FROM conversations 
                WHERE user_id = ? 
                ORDER BY timestamp DESC 
                LIMIT ?
            ''', (user_id, limit))
            
            entries = []
            for row in cursor.fetchall():
                # Parse tools_used JSON
                tools_used = []
                tools_data = json.loads(row['tools_used_json'])
                for tool_data in tools_data:
                    tools_used.append(ToolUsage(**tool_data))
                
                entry = ConversationEntry(
                    conversation_id=row['conversation_id'],
                    message_id=row['message_id'],
                    timestamp=datetime.fromisoformat(row['timestamp']),
                    user_id=row['user_id'],
                    username=row['username'],
                    first_name=row['first_name'],
                    last_name=row['last_name'],
                    user_message=row['user_message'],
                    agent_response=row['agent_response'],
                    agent_reasoning=row['agent_reasoning'],
                    tools_used=tools_used,
                    processing_time_ms=row['processing_time_ms'],
                    rate_limited=bool(row['rate_limited']),
                    error_occurred=bool(row['error_occurred']),
                    error_details=row['error_details'],
                    session_message_count=row['session_message_count'],
                    conversation_length_minutes=row['conversation_length_minutes']
                )
                entries.append(entry)
            
            return entries
    
    def get_usage_statistics(self, days: int = 30) -> Dict[str, Any]:
        """
        Get usage statistics for the specified time period.
        
        Args:
            days: Number of days to analyze
            
        Returns:
            Dictionary with usage statistics
        """
        cutoff_date = (datetime.now() - timedelta(days=days)).isoformat()
        
        with sqlite3.connect(self.db_path) as conn:
            # Total conversations
            total_conversations = conn.execute('''
                SELECT COUNT(*) FROM conversations 
                WHERE timestamp >= ?
            ''', (cutoff_date,)).fetchone()[0]
            
            # Unique users
            unique_users = conn.execute('''
                SELECT COUNT(DISTINCT user_id) FROM conversations 
                WHERE timestamp >= ?
            ''', (cutoff_date,)).fetchone()[0]
            
            # Top tools used
            top_tools = conn.execute('''
                SELECT tool_name, COUNT(*) as usage_count
                FROM tool_usage 
                WHERE timestamp >= ?
                GROUP BY tool_name 
                ORDER BY usage_count DESC
            ''', (cutoff_date,)).fetchall()
            
            # Average processing time
            avg_processing_time = conn.execute('''
                SELECT AVG(processing_time_ms) FROM conversations 
                WHERE timestamp >= ?
            ''', (cutoff_date,)).fetchone()[0]
            
            # Error rate
            error_count = conn.execute('''
                SELECT COUNT(*) FROM conversations 
                WHERE timestamp >= ? AND error_occurred = 1
            ''', (cutoff_date,)).fetchone()[0]
            
            # Rate limiting incidents
            rate_limited_count = conn.execute('''
                SELECT COUNT(*) FROM conversations 
                WHERE timestamp >= ? AND rate_limited = 1
            ''', (cutoff_date,)).fetchone()[0]
            
            return {
                'period_days': days,
                'total_conversations': total_conversations,
                'unique_users': unique_users,
                'top_tools': [{'tool': row[0], 'count': row[1]} for row in top_tools],
                'avg_processing_time_ms': round(avg_processing_time or 0, 2),
                'error_rate': round((error_count / max(total_conversations, 1)) * 100, 2),
                'rate_limited_conversations': rate_limited_count,
                'rate_limiting_rate': round((rate_limited_count / max(total_conversations, 1)) * 100, 2)
            }
    
    def export_conversations_csv(self, output_path: str, user_id: Optional[int] = None, 
                                days: Optional[int] = None, limit: Optional[int] = None):
        """
        Export conversations to CSV format for analysis.
        
        Args:
            output_path: Path to save the CSV file
            user_id: Optional user ID to filter by
            days: Optional number of days to include
            limit: Maximum number of records to export (uses config default if None)
        """
        if limit is None:
            limit = self.config.export.max_records_csv
        import csv
        
        query = "SELECT * FROM conversations"
        params = []
        conditions = []
        
        if user_id:
            conditions.append("user_id = ?")
            params.append(user_id)
        
        if days:
            cutoff_date = (datetime.now() - timedelta(days=days)).isoformat()
            conditions.append("timestamp >= ?")
            params.append(cutoff_date)
        
        if conditions:
            query += " WHERE " + " AND ".join(conditions)
        
        query += " ORDER BY timestamp LIMIT ?"
        params.append(limit)
        
        with sqlite3.connect(self.db_path) as conn:
            conn.row_factory = sqlite3.Row
            cursor = conn.execute(query, params)
            
            with open(output_path, 'w', newline='', encoding='utf-8') as csvfile:
                writer = csv.writer(csvfile)
                
                # Write header
                writer.writerow([
                    'timestamp', 'user_id', 'username', 'first_name', 'last_name',
                    'user_message', 'agent_response', 'agent_reasoning',
                    'tools_used_count', 'processing_time_ms', 'rate_limited',
                    'error_occurred', 'session_message_count'
                ])
                
                # Write data
                for row in cursor:
                    tools_count = len(json.loads(row['tools_used_json']))
                    writer.writerow([
                        row['timestamp'], row['user_id'], row['username'],
                        row['first_name'], row['last_name'], row['user_message'],
                        row['agent_response'], row['agent_reasoning'],
                        tools_count, row['processing_time_ms'], row['rate_limited'],
                        row['error_occurred'], row['session_message_count']
                    ])
    
    def generate_audit_report(self, output_path: str, days: int = 7):
        """
        Generate a comprehensive audit report.
        
        Args:
            output_path: Path to save the HTML report
            days: Number of days to include in the report
        """
        stats = self.get_usage_statistics(days)
        
        html_content = f"""
        <!DOCTYPE html>
        <html>
        <head>
            <title>Omotenashi Conversation Audit Report</title>
            <style>
                body {{ font-family: Arial, sans-serif; margin: 40px; }}
                .header {{ background-color: #f0f8ff; padding: 20px; border-radius: 10px; }}
                .stat-box {{ display: inline-block; margin: 10px; padding: 15px; 
                           background-color: #f9f9f9; border-radius: 5px; min-width: 150px; }}
                .tool-list {{ margin: 10px 0; }}
                .error {{ color: #d32f2f; }}
                .success {{ color: #388e3c; }}
                table {{ border-collapse: collapse; width: 100%; margin: 20px 0; }}
                th, td {{ border: 1px solid #ddd; padding: 8px; text-align: left; }}
                th {{ background-color: #f2f2f2; }}
            </style>
        </head>
        <body>
            <div class="header">
                <h1>🎌 Omotenashi Conversation Audit Report</h1>
                <p>Generated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}</p>
                <p>Period: Last {days} days</p>
            </div>
            
            <h2>📊 Usage Statistics</h2>
            <div class="stat-box">
                <h3>{stats['total_conversations']}</h3>
                <p>Total Conversations</p>
            </div>
            <div class="stat-box">
                <h3>{stats['unique_users']}</h3>
                <p>Unique Users</p>
            </div>
            <div class="stat-box">
                <h3>{stats['avg_processing_time_ms']}ms</h3>
                <p>Avg Processing Time</p>
            </div>
            <div class="stat-box">
                <h3 class="{'error' if stats['error_rate'] > 5 else 'success'}">{stats['error_rate']}%</h3>
                <p>Error Rate</p>
            </div>
            
            <h2>🔧 Tool Usage</h2>
            <table>
                <tr><th>Tool Name</th><th>Usage Count</th><th>Percentage</th></tr>
        """
        
        total_tool_usage = sum(tool['count'] for tool in stats['top_tools'])
        for tool in stats['top_tools']:
            percentage = (tool['count'] / max(total_tool_usage, 1)) * 100
            html_content += f"""
                <tr>
                    <td>{tool['tool']}</td>
                    <td>{tool['count']}</td>
                    <td>{percentage:.1f}%</td>
                </tr>
            """
        
        html_content += """
            </table>
            
            <h2>⚠️ Issues & Monitoring</h2>
            <ul>
        """
        
        if stats['error_rate'] > 5:
            html_content += f"<li class='error'>High error rate: {stats['error_rate']}%</li>"
        
        if stats['rate_limiting_rate'] > 10:
            html_content += f"<li class='error'>High rate limiting: {stats['rate_limiting_rate']}%</li>"
        
        if stats['avg_processing_time_ms'] > 5000:
            html_content += f"<li class='error'>Slow processing time: {stats['avg_processing_time_ms']}ms</li>"
        
        html_content += """
            </ul>
            
            <h2>📋 Recommendations</h2>
            <ul>
                <li>Monitor tool performance and optimize slow-running tools</li>
                <li>Review high-error conversations for common patterns</li>
                <li>Analyze user satisfaction based on conversation flow</li>
                <li>Consider expanding rate limits if legitimate usage is being blocked</li>
            </ul>
        </body>
        </html>
        """
        
        with open(output_path, 'w', encoding='utf-8') as f:
            f.write(html_content)


# Global logger instance
_conversation_logger = None

def get_conversation_logger() -> ConversationLogger:
    """Get or create the global conversation logger instance."""
    global _conversation_logger
    if _conversation_logger is None:
        _conversation_logger = ConversationLogger()
    return _conversation_logger