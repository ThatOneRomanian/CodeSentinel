"""
Configuration persistence helpers for the CodeSentinel Phase 3 API.

Provides shared config serialization, deserialization, and platform-aware storage
for the GUI <-> CLI SharedConfig model.
"""

import json
import logging
import os
import pathlib
from dataclasses import asdict
from datetime import datetime
from typing import Any, Dict, List, Optional

from .models import (
    SharedConfig,
    ScanConfig,
    ScanOptions,
    UserPreferences,
    ExportSettings,
    NotificationSettings,
    AIProviderConfig,
    ProjectHistory,
)

logger = logging.getLogger(__name__)


class ConfigManager:
    """Manages loading and saving the SharedConfig used by GUI and CLI."""

    def __init__(self, config_path: Optional[pathlib.Path] = None):
        self.config_path = config_path or self._get_default_config_path()
        self._config: Optional[SharedConfig] = None

    def _get_default_config_path(self) -> pathlib.Path:
        """Get platform-specific default configuration path."""
        if os.name == "nt":
            base = pathlib.Path(os.environ.get("APPDATA", pathlib.Path.home()))
        else:
            base = pathlib.Path.home() / ".config"
        return base / "codesentinel" / "config.json"

    def load_config(self) -> SharedConfig:
        """Load SharedConfig from disk (returns defaults on failure)."""
        if self.config_path.exists():
            try:
                with open(self.config_path, "r", encoding="utf-8") as f:
                    data = json.load(f)
                config = self._deserialize_config(data)
                self._config = config
                return config
            except Exception as exc:
                logger.warning("Failed to load SharedConfig, using defaults: %s", exc)
        return SharedConfig()

    def save_config(self, config: SharedConfig) -> bool:
        """Persist SharedConfig to disk."""
        try:
            self.config_path.parent.mkdir(parents=True, exist_ok=True)
            with open(self.config_path, "w", encoding="utf-8") as f:
                json.dump(self._serialize_config(config), f, indent=2)
            self._config = config
            return True
        except Exception as exc:
            logger.error("Failed to save SharedConfig: %s", exc)
            return False

    def sync_with_cli(self) -> bool:
        """
        Synchronize the current config with the CLI's defaults.

        For now this reloads the persisted config and rewrites it,
        ensuring both sides are aligned.
        """
        try:
            config = self.load_config()
            return self.save_config(config)
        except Exception as exc:
            logger.warning("Failed to sync SharedConfig: %s", exc)
            return False

    def _serialize_config(self, config: SharedConfig) -> Dict[str, Any]:
        """Convert SharedConfig into JSON-serializable dict."""
        return {
            "scan_defaults": self._serialize_scan_config(config.scan_defaults),
            "ai_providers": {
                name: asdict(cfg) for name, cfg in config.ai_providers.items()
            },
            "user_preferences": self._serialize_dataclass(config.user_preferences),
            "recent_projects": [
                {
                    "project_path": str(entry.project_path),
                    "last_scan_date": entry.last_scan_date,
                    "total_findings": entry.total_findings,
                    "severity_breakdown": entry.severity_breakdown,
                    "scan_count": entry.scan_count,
                }
                for entry in config.recent_projects
            ],
            "export_settings": self._serialize_dataclass(config.export_settings),
            "notification_settings": self._serialize_dataclass(config.notification_settings),
        }

    def _serialize_scan_config(self, scan_config: ScanConfig) -> Dict[str, Any]:
        result = asdict(scan_config)
        result["target_path"] = str(scan_config.target_path)
        result["scan_options"] = self._serialize_dataclass(scan_config.scan_options)
        return result

    def _serialize_dataclass(self, instance: Any) -> Dict[str, Any]:
        normalized = asdict(instance)
        return self._normalize_paths(normalized)

    def _normalize_paths(self, value: Any) -> Any:
        """Recursively convert pathlib.Path values to strings."""
        if isinstance(value, pathlib.Path):
            return str(value)
        if isinstance(value, dict):
            return {k: self._normalize_paths(v) for k, v in value.items()}
        if isinstance(value, list):
            return [self._normalize_paths(v) for v in value]
        return value

    def _deserialize_config(self, raw: Dict[str, Any]) -> SharedConfig:
        config = SharedConfig()

        scan_defaults = raw.get("scan_defaults")
        if scan_defaults:
            config.scan_defaults = self._dict_to_scan_config(scan_defaults)

        ai_providers = raw.get("ai_providers", {})
        for name, payload in ai_providers.items():
            config.ai_providers[name] = AIProviderConfig(
                provider_name=payload.get("provider_name", name),
                api_key=payload.get("api_key"),
                base_url=payload.get("base_url"),
                timeout=payload.get("timeout", 30),
                max_retries=payload.get("max_retries", 3),
                enabled=payload.get("enabled", True),
            )

        user_prefs = raw.get("user_preferences")
        if user_prefs:
            config.user_preferences = UserPreferences(
                theme=user_prefs.get("theme", "dark"),
                default_severity_filter=user_prefs.get(
                    "default_severity_filter", ["high", "medium", "critical"]
                ),
                auto_save_reports=user_prefs.get("auto_save_reports", False),
                max_history_items=user_prefs.get("max_history_items", 50),
                language=user_prefs.get("language", "en"),
                notification_settings=NotificationSettings(
                    enable_toasts=user_prefs.get("notification_settings", {}).get("enable_toasts", True),
                    enable_email_alerts=user_prefs.get("notification_settings", {}).get("enable_email_alerts", False),
                    alert_level=user_prefs.get("notification_settings", {}).get("alert_level", "high"),
                ),
            )

        export_settings = raw.get("export_settings")
        if export_settings:
            config.export_settings = ExportSettings(
                default_format=export_settings.get("default_format", "markdown"),
                auto_attach_history=export_settings.get("auto_attach_history", False),
                legacy_output_path=pathlib.Path(export_settings["legacy_output_path"])
                if export_settings.get("legacy_output_path")
                else None,
            )

        notification_settings = raw.get("notification_settings")
        if notification_settings:
            config.notification_settings = NotificationSettings(
                enable_toasts=notification_settings.get("enable_toasts", True),
                enable_email_alerts=notification_settings.get("enable_email_alerts", False),
                alert_level=notification_settings.get("alert_level", "high"),
            )

        recent_projects = raw.get("recent_projects", [])
        for entry in recent_projects:
            try:
                config.recent_projects.append(
                    ProjectHistory(
                        project_path=pathlib.Path(entry.get("project_path", ".")),
                        last_scan_date=entry.get("last_scan_date", datetime.utcnow().isoformat()),
                        total_findings=entry.get("total_findings", 0),
                        severity_breakdown=entry.get("severity_breakdown", {}),
                        scan_count=entry.get("scan_count", 1),
                    )
                )
            except Exception:
                continue

        return config

    def _dict_to_scan_config(self, raw: Dict[str, Any]) -> ScanConfig:
        scan_options_data = raw.get("scan_options", {})
        scan_options = ScanOptions(
            include_patterns=scan_options_data.get("include_patterns", ScanOptions().include_patterns),
            exclude_patterns=scan_options_data.get("exclude_patterns", ScanOptions().exclude_patterns),
            max_file_size=scan_options_data.get("max_file_size", 10485760),
            scan_depth=scan_options_data.get("scan_depth"),
            enable_entropy_analysis=scan_options_data.get(
                "enable_entropy_analysis", True
            ),
            confidence_threshold=scan_options_data.get("confidence_threshold", 0.5),
            enable_profiling=scan_options_data.get("enable_profiling", False),
        )

        return ScanConfig(
            target_path=pathlib.Path(raw.get("target_path", ".")),
            enable_ai=raw.get("enable_ai", False),
            llm_provider=raw.get("llm_provider", "deepseek"),
            output_format=raw.get("output_format", "gui_enhanced"),
            scan_options=scan_options,
            enable_debug=raw.get("enable_debug", False),
        )