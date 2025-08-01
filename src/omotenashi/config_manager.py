"""
Configuration Manager for Omotenashi
-----------------------------------
Centralized configuration management for the Omotenashi system,
providing type-safe access to configuration values with defaults.
"""

import yaml
import os
from pathlib import Path
from typing import Dict, Any, Optional
from dataclasses import dataclass


@dataclass
class RateLimitingConfig:
    """Rate limiting configuration."""
    messages_per_minute: int = 10
    timeout_seconds: int = 60


@dataclass
class SessionConfig:
    """Session management configuration."""
    timeout_hours: int = 2
    max_concurrent_sessions: int = 50
    cleanup_threshold: int = 50


@dataclass
class DatabaseConfig:
    """Database configuration."""
    path: str = "logs/conversations.db"
    connection_timeout_seconds: int = 30
    max_connections: int = 10
    enable_wal_mode: bool = True


@dataclass
class ExportConfig:
    """Export configuration."""
    max_records_csv: int = 10000
    max_records_html: int = 5000
    default_days_history: int = 7


@dataclass
class MonitoringConfig:
    """Performance monitoring configuration."""
    max_error_rate_percent: float = 5.0
    max_processing_time_ms: float = 5000.0
    max_rate_limiting_percent: float = 10.0
    alert_on_high_usage: bool = True


@dataclass
class SecurityConfig:
    """Security configuration."""
    enable_file_permissions: bool = True
    log_sensitive_data: bool = False
    encrypt_user_data: bool = False


@dataclass
class MemoryConfig:
    """Memory management configuration."""
    window_size: int = 10
    auto_cleanup: bool = True
    cleanup_interval_hours: int = 24


@dataclass
class LoggingConfig:
    """Complete logging configuration."""
    rate_limiting: RateLimitingConfig
    session: SessionConfig
    database: DatabaseConfig
    export: ExportConfig
    monitoring: MonitoringConfig
    security: SecurityConfig
    memory: MemoryConfig


class ConfigManager:
    """Manages configuration loading and access."""
    
    def __init__(self, config_path: Optional[str] = None):
        """Initialize configuration manager.
        
        Args:
            config_path: Path to configuration file. If None, uses default.
        """
        if config_path is None:
            config_path = Path(__file__).parent / "config" / "logging_config.yaml"
        
        self.config_path = Path(config_path)
        self._config_data = None
        self._logging_config = None
    
    def _load_config(self) -> Dict[str, Any]:
        """Load configuration from YAML file."""
        if self._config_data is None:
            try:
                with open(self.config_path, 'r') as f:
                    self._config_data = yaml.safe_load(f)
            except FileNotFoundError:
                # Use default configuration if file not found
                self._config_data = {}
            except Exception as e:
                raise ValueError(f"Failed to load configuration: {e}")
        
        return self._config_data
    
    def get_logging_config(self) -> LoggingConfig:
        """Get complete logging configuration with defaults."""
        if self._logging_config is None:
            config_data = self._load_config()
            
            # Create configuration objects with defaults
            rate_limiting = RateLimitingConfig(
                messages_per_minute=config_data.get('rate_limiting', {}).get('messages_per_minute', 10),
                timeout_seconds=config_data.get('rate_limiting', {}).get('timeout_seconds', 60)
            )
            
            session = SessionConfig(
                timeout_hours=config_data.get('session', {}).get('timeout_hours', 2),
                max_concurrent_sessions=config_data.get('session', {}).get('max_concurrent_sessions', 50),
                cleanup_threshold=config_data.get('session', {}).get('cleanup_threshold', 50)
            )
            
            database = DatabaseConfig(
                path=config_data.get('database', {}).get('path', 'logs/conversations.db'),
                connection_timeout_seconds=config_data.get('database', {}).get('connection_timeout_seconds', 30),
                max_connections=config_data.get('database', {}).get('max_connections', 10),
                enable_wal_mode=config_data.get('database', {}).get('enable_wal_mode', True)
            )
            
            export = ExportConfig(
                max_records_csv=config_data.get('export', {}).get('max_records_csv', 10000),
                max_records_html=config_data.get('export', {}).get('max_records_html', 5000),
                default_days_history=config_data.get('export', {}).get('default_days_history', 7)
            )
            
            monitoring = MonitoringConfig(
                max_error_rate_percent=config_data.get('monitoring', {}).get('max_error_rate_percent', 5.0),
                max_processing_time_ms=config_data.get('monitoring', {}).get('max_processing_time_ms', 5000.0),
                max_rate_limiting_percent=config_data.get('monitoring', {}).get('max_rate_limiting_percent', 10.0),
                alert_on_high_usage=config_data.get('monitoring', {}).get('alert_on_high_usage', True)
            )
            
            security = SecurityConfig(
                enable_file_permissions=config_data.get('security', {}).get('enable_file_permissions', True),
                log_sensitive_data=config_data.get('security', {}).get('log_sensitive_data', False),
                encrypt_user_data=config_data.get('security', {}).get('encrypt_user_data', False)
            )
            
            memory = MemoryConfig(
                window_size=config_data.get('memory', {}).get('window_size', 10),
                auto_cleanup=config_data.get('memory', {}).get('auto_cleanup', True),
                cleanup_interval_hours=config_data.get('memory', {}).get('cleanup_interval_hours', 24)
            )
            
            self._logging_config = LoggingConfig(
                rate_limiting=rate_limiting,
                session=session,
                database=database,
                export=export,
                monitoring=monitoring,
                security=security,
                memory=memory
            )
        
        return self._logging_config
    
    def get_value(self, key_path: str, default: Any = None) -> Any:
        """Get a configuration value by dot-separated key path.
        
        Args:
            key_path: Dot-separated path to the configuration value
            default: Default value if key not found
            
        Returns:
            Configuration value or default
            
        Examples:
            get_value('rate_limiting.messages_per_minute')
            get_value('database.path', 'logs/conversations.db')
        """
        config_data = self._load_config()
        
        keys = key_path.split('.')
        current = config_data
        
        for key in keys:
            if isinstance(current, dict) and key in current:
                current = current[key]
            else:
                return default
        
        return current
    
    def set_value(self, key_path: str, value: Any):
        """Set a configuration value by dot-separated key path.
        
        Args:
            key_path: Dot-separated path to the configuration value
            value: Value to set
        """
        config_data = self._load_config()
        
        keys = key_path.split('.')
        current = config_data
        
        # Navigate to the parent of the target key
        for key in keys[:-1]:
            if key not in current:
                current[key] = {}
            current = current[key]
        
        # Set the final value
        current[keys[-1]] = value
        
        # Clear cached configuration to force reload
        self._logging_config = None
    
    def reload(self):
        """Reload configuration from file."""
        self._config_data = None
        self._logging_config = None


# Global configuration manager instance
_config_manager = None


def get_config_manager() -> ConfigManager:
    """Get or create the global configuration manager instance."""
    global _config_manager
    if _config_manager is None:
        _config_manager = ConfigManager()
    return _config_manager


def get_logging_config() -> LoggingConfig:
    """Get the logging configuration."""
    return get_config_manager().get_logging_config()


# Environment variable overrides
def apply_env_overrides(config: LoggingConfig) -> LoggingConfig:
    """Apply environment variable overrides to configuration.
    
    Args:
        config: Base configuration
        
    Returns:
        Configuration with environment overrides applied
    """
    # Rate limiting overrides
    if os.getenv('OMOTENASHI_RATE_LIMIT_MESSAGES'):
        config.rate_limiting.messages_per_minute = int(os.getenv('OMOTENASHI_RATE_LIMIT_MESSAGES'))
    
    if os.getenv('OMOTENASHI_SESSION_TIMEOUT_HOURS'):
        config.session.timeout_hours = int(os.getenv('OMOTENASHI_SESSION_TIMEOUT_HOURS'))
    
    if os.getenv('OMOTENASHI_DB_PATH'):
        config.database.path = os.getenv('OMOTENASHI_DB_PATH')
    
    if os.getenv('OMOTENASHI_MAX_CSV_RECORDS'):
        config.export.max_records_csv = int(os.getenv('OMOTENASHI_MAX_CSV_RECORDS'))
    
    return config