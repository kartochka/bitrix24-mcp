"""Модуль с контейнером зависимостей приложения.

Предоставляет единую точку инициализации и получения зависимостей.
"""

from wireup import create_container

from src import application
from src.config import SettingsManager

from .bitrix import repository_factory
from .mcp import server

container = create_container(
    parameters={'bitrix_webhook_url': SettingsManager.get().BITRIX_WEBHOOK_URL},
    service_modules=[server, repository_factory, application],
)
