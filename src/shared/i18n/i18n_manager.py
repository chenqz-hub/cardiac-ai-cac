"""
Internationalization (i18n) Manager for Cardiac ML Research
国际化管理器

Provides multi-language support for UI menus and messages.

Per WEEK7_PLUS_DEPLOYMENT_PLAN.md Section 0 i18n guidelines:
- Code/logs: ENGLISH ONLY (avoid encoding errors in deployment)
- UI menus: Chinese/English toggle (use this i18n system)
- Documentation: Chinese preferred (for doctors/technicians)

Supported languages:
- zh: Chinese (Simplified) - Default for medical staff
- en: English - Alternative for international use

Author: Cardiac ML Research Team
Created: 2025-10-19
"""

import os
from pathlib import Path
from typing import Dict, Any, Optional
import yaml
import logging

logger = logging.getLogger(__name__)


class I18nManager:
    """
    Internationalization manager for multi-language UI support

    Loads and manages localized messages from YAML files.

    Example:
        >>> i18n = I18nManager(language='zh')
        >>> print(i18n.get('main_menu.title'))
        心脏影像多模态分析系统

        >>> print(i18n.get('common.yes'))
        是

        >>> i18n.set_language('en')
        >>> print(i18n.get('common.yes'))
        Yes
    """

    SUPPORTED_LANGUAGES = ['zh', 'en']
    DEFAULT_LANGUAGE = 'zh'  # Chinese default for medical staff

    def __init__(self, language: Optional[str] = None, messages_dir: Optional[Path] = None):
        """
        Initialize i18n manager

        Args:
            language: Language code ('zh' or 'en'). Defaults to 'zh'.
            messages_dir: Directory containing message YAML files.
                         If None, uses default location (shared/i18n/)
        """
        # Determine messages directory
        if messages_dir is None:
            # Default: shared/i18n/ (same directory as this file)
            messages_dir = Path(__file__).parent
        self.messages_dir = messages_dir

        # Set language
        self._language = self._validate_language(language or self.DEFAULT_LANGUAGE)
        self._messages: Dict[str, Any] = {}
        self._fallback_messages: Dict[str, Any] = {}

        # Load messages
        self._load_messages()

        logger.info(f"I18nManager initialized with language: {self._language}")

    def _validate_language(self, language: str) -> str:
        """Validate and return language code"""
        if language not in self.SUPPORTED_LANGUAGES:
            logger.warning(f"Unsupported language '{language}', using default '{self.DEFAULT_LANGUAGE}'")
            return self.DEFAULT_LANGUAGE
        return language

    def _load_messages(self):
        """Load messages for current language and fallback (English)"""
        # Load current language
        messages_file = self.messages_dir / f'messages_{self._language}.yaml'

        if not messages_file.exists():
            logger.error(f"Messages file not found: {messages_file}")
            self._messages = {}
        else:
            try:
                with open(messages_file, 'r', encoding='utf-8') as f:
                    self._messages = yaml.safe_load(f) or {}
                logger.debug(f"Loaded messages from {messages_file}")
            except Exception as e:
                logger.error(f"Failed to load messages from {messages_file}: {e}")
                self._messages = {}

        # Load fallback (English) if current language is not English
        if self._language != 'en':
            fallback_file = self.messages_dir / 'messages_en.yaml'
            if fallback_file.exists():
                try:
                    with open(fallback_file, 'r', encoding='utf-8') as f:
                        self._fallback_messages = yaml.safe_load(f) or {}
                    logger.debug(f"Loaded fallback messages from {fallback_file}")
                except Exception as e:
                    logger.error(f"Failed to load fallback messages: {e}")
                    self._fallback_messages = {}
            else:
                self._fallback_messages = {}
        else:
            self._fallback_messages = {}

    def get(self, key: str, default: Optional[str] = None, **kwargs) -> str:
        """
        Get localized message by key

        Supports nested keys using dot notation (e.g., 'main_menu.title')
        Supports string formatting with kwargs.

        Args:
            key: Message key (dot notation for nested keys)
            default: Default value if key not found
            **kwargs: Format parameters for string interpolation

        Returns:
            Localized message string

        Example:
            >>> i18n.get('processing.progress.current')
            '当前进度'

            >>> i18n.get('time.estimated', count=5)
            'estimated 5 minutes'
        """
        # Split key into parts
        parts = key.split('.')

        # Try current language
        value = self._get_nested(self._messages, parts)

        # Try fallback if not found
        if value is None and self._fallback_messages:
            value = self._get_nested(self._fallback_messages, parts)

        # Use default if still not found
        if value is None:
            if default is not None:
                value = default
            else:
                logger.warning(f"Message key not found: {key}")
                value = f"[{key}]"  # Return key wrapped in brackets

        # Format with kwargs if provided
        if kwargs and isinstance(value, str):
            try:
                value = value.format(**kwargs)
            except KeyError as e:
                logger.warning(f"Missing format parameter for key '{key}': {e}")

        return str(value)

    def _get_nested(self, data: Dict, keys: list) -> Optional[Any]:
        """Get nested dictionary value using list of keys"""
        current = data
        for key in keys:
            if isinstance(current, dict) and key in current:
                current = current[key]
            else:
                return None
        return current

    def set_language(self, language: str):
        """
        Change current language

        Args:
            language: Language code ('zh' or 'en')
        """
        new_language = self._validate_language(language)

        if new_language != self._language:
            self._language = new_language
            self._load_messages()
            logger.info(f"Language changed to: {self._language}")

    def get_language(self) -> str:
        """Get current language code"""
        return self._language

    def get_available_languages(self) -> list:
        """Get list of supported languages"""
        return self.SUPPORTED_LANGUAGES.copy()

    def exists(self, key: str) -> bool:
        """
        Check if message key exists

        Args:
            key: Message key

        Returns:
            True if key exists in current or fallback messages
        """
        parts = key.split('.')
        return (self._get_nested(self._messages, parts) is not None or
                self._get_nested(self._fallback_messages, parts) is not None)

    def get_all(self, prefix: Optional[str] = None) -> Dict[str, Any]:
        """
        Get all messages, optionally filtered by prefix

        Args:
            prefix: Optional key prefix (e.g., 'main_menu')

        Returns:
            Dictionary of messages
        """
        if prefix:
            parts = prefix.split('.')
            return self._get_nested(self._messages, parts) or {}
        else:
            return self._messages.copy()

    def __call__(self, key: str, default: Optional[str] = None, **kwargs) -> str:
        """
        Shorthand for get()

        Allows usage like: i18n('main_menu.title')
        """
        return self.get(key, default, **kwargs)

    def __repr__(self):
        return f"I18nManager(language='{self._language}', messages_loaded={len(self._messages) > 0})"


# Global singleton instance (can be imported)
_default_instance: Optional[I18nManager] = None


def get_i18n(language: Optional[str] = None) -> I18nManager:
    """
    Get global I18nManager instance (singleton pattern)

    Args:
        language: Optional language override. If None, uses existing instance or creates default.

    Returns:
        I18nManager instance
    """
    global _default_instance

    if _default_instance is None or language is not None:
        _default_instance = I18nManager(language=language)

    return _default_instance


def t(key: str, default: Optional[str] = None, **kwargs) -> str:
    """
    Global translation function (shorthand)

    Example:
        >>> from shared.i18n.i18n_manager import t
        >>> print(t('main_menu.title'))

    Args:
        key: Message key
        default: Default value
        **kwargs: Format parameters

    Returns:
        Localized message
    """
    return get_i18n().get(key, default, **kwargs)


if __name__ == '__main__':
    # Example usage and testing
    print("=== I18n Manager Test ===\n")

    # Test Chinese (default)
    print("--- Chinese (ZH) ---")
    i18n_zh = I18nManager(language='zh')
    print(f"Language: {i18n_zh.get_language()}")
    print(f"Main menu title: {i18n_zh.get('main_menu.title')}")
    print(f"Common yes: {i18n_zh.get('common.yes')}")
    print(f"Processing status: {i18n_zh.get('processing.status.initializing')}")
    print(f"Module name: {i18n_zh.get('modules.cardiac_calcium_scoring.name')}")

    # Test English
    print("\n--- English (EN) ---")
    i18n_en = I18nManager(language='en')
    print(f"Language: {i18n_en.get_language()}")
    print(f"Main menu title: {i18n_en.get('main_menu.title')}")
    print(f"Common yes: {i18n_en.get('common.yes')}")
    print(f"Processing status: {i18n_en.get('processing.status.initializing')}")
    print(f"Module name: {i18n_en.get('modules.cardiac_calcium_scoring.name')}")

    # Test language switching
    print("\n--- Language Switching ---")
    i18n = I18nManager(language='zh')
    print(f"Initial: {i18n.get('common.yes')}")
    i18n.set_language('en')
    print(f"After switch to EN: {i18n.get('common.yes')}")
    i18n.set_language('zh')
    print(f"After switch to ZH: {i18n.get('common.yes')}")

    # Test missing keys
    print("\n--- Missing Keys ---")
    print(f"Non-existent key: {i18n.get('this.does.not.exist')}")
    print(f"With default: {i18n.get('this.does.not.exist', default='Default Value')}")

    # Test global function
    print("\n--- Global Function ---")
    print(f"Using t(): {t('main_menu.title')}")

    # Test exists
    print("\n--- Key Existence ---")
    print(f"'main_menu.title' exists: {i18n.exists('main_menu.title')}")
    print(f"'nonexistent.key' exists: {i18n.exists('nonexistent.key')}")

    # Test get_all
    print("\n--- Get All (prefix) ---")
    common_messages = i18n.get_all('common')
    print(f"Common messages: {list(common_messages.keys())[:5]}...")
