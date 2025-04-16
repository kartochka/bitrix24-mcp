"""Модуль конфигурации приложения.

Предоставляет настройки приложения через переменные окружения.
"""

import os
from dataclasses import dataclass
from typing import ClassVar


@dataclass(frozen=True, slots=True)
class Settings:
    """Настройки приложения.

    :param bitrix_webhook_url: URL вебхука Bitrix24.
    :param log_level: Уровень логирования (DEBUG, INFO, WARNING, ERROR, CRITICAL).
    """

    BITRIX_WEBHOOK_URL: str
    LOG_LEVEL: str = 'INFO'


class SettingsManager:
    """Менеджер настроек приложения.
    Реализует паттерн Singleton для управления настройками.
    """

    _instance: ClassVar[Settings | None] = None

    @classmethod
    def init(cls) -> Settings:
        """Инициализация настроек приложения.

        :return: Экземпляр настроек.
        :raises ValueError: Если не указан URL вебхука.
        """
        if cls._instance is None:
            webhook_url = os.getenv('BITRIX_WEBHOOK_URL')
            log_level = os.getenv('LOG_LEVEL', 'INFO')

            if not webhook_url:
                msg = (
                    'Не указана переменная окружения BITRIX_WEBHOOK_URL. '
                    'Пожалуйста, укажите URL вебхука Bitrix24.',
                )
                raise ValueError(msg)

            cls._instance = Settings(
                BITRIX_WEBHOOK_URL=webhook_url,
                LOG_LEVEL=log_level,
            )
        return cls._instance

    @classmethod
    def get(cls) -> Settings:
        """Получение текущих настроек приложения.

        :return: Экземпляр настроек.
        """
        if cls._instance is None:
            return cls.init()
        return cls._instance
