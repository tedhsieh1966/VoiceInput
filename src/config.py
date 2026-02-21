import json
import os
from pathlib import Path
from typing import Dict, Any, Optional


class ConfigManager:
    def __init__(self, config_file: str = "config.json"):
        self.config_file = Path(config_file)
        self.default_config = {
  "language": "zh-TW",
  "hot_key": "ctrl+shift+i"
}
        self.config = self.load_config()

    def load_config(self) -> Dict[str, Any]:
        """加載配置"""
        if self.config_file.exists():
            try:
                with open(self.config_file, 'r', encoding='utf-8') as f:
                    user_config = json.load(f)
                    # 深度合併配置
                    return self._deep_merge(self.default_config, user_config)
            except Exception as e:
                print(f"加載配置失敗，使用默認配置: {e}")

        return self.default_config.copy()

    def save_config(self):
        """保存配置"""
        try:
            self.config_file.parent.mkdir(parents=True, exist_ok=True)
            with open(self.config_file, 'w', encoding='utf-8') as f:
                json.dump(self.config, f, ensure_ascii=False, indent=2)
        except Exception as e:
            print(f"保存配置失敗: {e}")

    def get_hot_key(self):
        return self.get("hot_key")

    def set_hot_key(self, hot_key):
        self.set("hot_key", hot_key)

    def get(self, key: str, default: Any = None) -> Any:
        """獲取配置值"""
        keys = key.split('.')
        value = self.config
        for k in keys:
            if isinstance(value, dict) and k in value:
                value = value[k]
            else:
                return default
        return value

    def set(self, key: str, value: Any):
        """設置配置值"""
        keys = key.split('.')
        config_ref = self.config

        for k in keys[:-1]:
            if k not in config_ref or not isinstance(config_ref[k], dict):
                config_ref[k] = {}
            config_ref = config_ref[k]

        config_ref[keys[-1]] = value
        self.save_config()

    def _deep_merge(self, base: Dict, update: Dict) -> Dict:
        """深度合併字典"""
        result = base.copy()
        for key, value in update.items():
            if isinstance(value, dict) and key in result and isinstance(result[key], dict):
                result[key] = self._deep_merge(result[key], value)
            else:
                result[key] = value
        return result
