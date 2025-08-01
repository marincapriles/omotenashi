#!/usr/bin/env python3
"""
Audit Report Generator for Omotenashi Telegram Bot
--------------------------------------------------
This script generates comprehensive audit reports from conversation logs,
including usage statistics, tool performance, and user interaction patterns.
"""

import sys
import argparse
from pathlib import Path
from datetime import datetime, timedelta

# Add parent directory to path for imports
sys.path.insert(0, str(Path(__file__).parent.parent))

from src.omotenashi.conversation_logger import get_conversation_logger


def generate_daily_report(output_dir: str = "reports"):
    """Generate daily audit report."""
    logger = get_conversation_logger()
    output_path = Path(output_dir)
    output_path.mkdir(exist_ok=True)
    
    date_str = datetime.now().strftime("%Y%m%d")
    report_file = output_path / f"omotenashi_audit_{date_str}.html"
    
    print(f"Generating daily audit report...")
    logger.generate_audit_report(str(report_file), days=1)
    print(f"✅ Report saved to: {report_file}")
    
    return report_file


def generate_weekly_report(output_dir: str = "reports"):
    """Generate weekly audit report."""
    logger = get_conversation_logger()
    output_path = Path(output_dir)
    output_path.mkdir(exist_ok=True)
    
    date_str = datetime.now().strftime("%Y%m%d")
    report_file = output_path / f"omotenashi_weekly_audit_{date_str}.html"
    
    print(f"Generating weekly audit report...")
    logger.generate_audit_report(str(report_file), days=7)
    print(f"✅ Report saved to: {report_file}")
    
    return report_file


def export_conversations_csv(days: int = None, user_id: int = None, output_dir: str = "reports"):
    """Export conversations to CSV for analysis."""
    logger = get_conversation_logger()
    output_path = Path(output_dir)
    output_path.mkdir(exist_ok=True)
    
    # Use config default if days not specified
    if days is None:
        try:
            from src.omotenashi.config_manager import get_logging_config
            config = get_logging_config()
            days = config.export.default_days_history
        except ImportError:
            days = 7  # Fallback default
    
    date_str = datetime.now().strftime("%Y%m%d")
    user_suffix = f"_user_{user_id}" if user_id else ""
    csv_file = output_path / f"omotenashi_conversations_{date_str}{user_suffix}.csv"
    
    print(f"Exporting conversations to CSV...")
    logger.export_conversations_csv(str(csv_file), user_id=user_id, days=days)
    print(f"✅ CSV exported to: {csv_file}")
    
    return csv_file


def print_usage_statistics(days: int = 7):
    """Print usage statistics to console."""
    logger = get_conversation_logger()
    
    print(f"\n🎌 Omotenashi Usage Statistics (Last {days} days)")
    print("=" * 60)
    
    stats = logger.get_usage_statistics(days)
    
    print(f"📊 Overview:")
    print(f"  • Total Conversations: {stats['total_conversations']}")
    print(f"  • Unique Users: {stats['unique_users']}")
    print(f"  • Average Processing Time: {stats['avg_processing_time_ms']}ms")
    print(f"  • Error Rate: {stats['error_rate']}%")
    print(f"  • Rate Limited Conversations: {stats['rate_limited_conversations']}")
    
    print(f"\n🔧 Tool Usage:")
    for tool in stats['top_tools'][:5]:  # Show top 5 tools
        percentage = (tool['count'] / max(sum(t['count'] for t in stats['top_tools']), 1)) * 100
        print(f"  • {tool['tool']}: {tool['count']} uses ({percentage:.1f}%)")
    
    if stats['error_rate'] > 5:
        print(f"\n⚠️  High error rate detected: {stats['error_rate']}%")
    
    if stats['rate_limiting_rate'] > 10:
        print(f"⚠️  High rate limiting: {stats['rate_limiting_rate']}%")
    
    print()


def show_recent_conversations(limit: int = 10, user_id: int = None):
    """Show recent conversations."""
    logger = get_conversation_logger()
    
    if user_id:
        conversations = logger.get_conversation_history(user_id, limit)
        print(f"\n📝 Recent Conversations for User {user_id} (Last {limit})")
    else:
        # Get conversations from database directly for all users
        import sqlite3
        with sqlite3.connect(logger.db_path) as conn:
            conn.row_factory = sqlite3.Row
            cursor = conn.execute('''
                SELECT * FROM conversations 
                ORDER BY timestamp DESC 
                LIMIT ?
            ''', (limit,))
            
            print(f"\n📝 Recent Conversations (Last {limit})")
            print("=" * 80)
            
            for row in cursor.fetchall():
                timestamp = datetime.fromisoformat(row['timestamp'])
                user_name = row['first_name'] or 'Unknown'
                if row['username']:
                    user_name += f" (@{row['username']})"
                
                print(f"\n🕐 {timestamp.strftime('%Y-%m-%d %H:%M:%S')} | User: {user_name}")
                print(f"👤 User: {row['user_message'][:100]}{'...' if len(row['user_message']) > 100 else ''}")
                print(f"🤖 Agent: {row['agent_response'][:100]}{'...' if len(row['agent_response']) > 100 else ''}")
                
                # Parse tools used
                import json
                tools_data = json.loads(row['tools_used_json'])
                if tools_data:
                    tool_names = [tool['tool_name'] for tool in tools_data]
                    print(f"🔧 Tools: {', '.join(tool_names)}")
                
                if row['error_occurred']:
                    print(f"❌ Error: {row['error_details']}")
                
                print(f"⏱️  Processing: {row['processing_time_ms']:.1f}ms")
            
            print()


def main():
    """Main entry point for the audit report generator."""
    parser = argparse.ArgumentParser(
        description="Generate audit reports for Omotenashi Telegram bot conversations"
    )
    
    parser.add_argument(
        'command',
        choices=['daily', 'weekly', 'stats', 'export', 'recent'],
        help='Type of report to generate'
    )
    
    parser.add_argument(
        '--days',
        type=int,
        default=7,
        help='Number of days to include (default: 7)'
    )
    
    parser.add_argument(
        '--user-id',
        type=int,
        help='Filter by specific user ID'
    )
    
    parser.add_argument(
        '--output-dir',
        default='reports',
        help='Output directory for reports (default: reports)'
    )
    
    parser.add_argument(
        '--limit',
        type=int,
        default=10,
        help='Limit for recent conversations (default: 10)'
    )
    
    args = parser.parse_args()
    
    try:
        if args.command == 'daily':
            generate_daily_report(args.output_dir)
            
        elif args.command == 'weekly':
            generate_weekly_report(args.output_dir)
            
        elif args.command == 'stats':
            print_usage_statistics(args.days)
            
        elif args.command == 'export':
            export_conversations_csv(args.days, args.user_id, args.output_dir)
            
        elif args.command == 'recent':
            show_recent_conversations(args.limit, args.user_id)
            
    except Exception as e:
        print(f"❌ Error generating report: {e}")
        sys.exit(1)


if __name__ == "__main__":
    main()