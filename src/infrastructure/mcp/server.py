"""Модуль с базовой реализацией MCP сервера.
Содержит основную реализацию Model Context Protocol сервера
для интеграции с Bitrix24.
"""

from collections.abc import Awaitable, Callable

from mcp.server.fastmcp import FastMCP
from wireup import service

from src.infrastructure.logging.logger import logger


@service
class BitrixMCPServer:
    """Базовая реализация MCP сервера для интеграции с Bitrix24.
    Предоставляет общую функциональность для работы с Model Context Protocol.
    """

    def __init__(self, server_name: str = "Bitrix24 MCP Server"):
        """Инициализация MCP сервера.
        :param server_name: Название сервера.
        """
        self._server = FastMCP(server_name)
        logger.info(f"Создан MCP сервер: {server_name}")

    def add_tool(
        self,
        func: Callable[..., Awaitable[str]],
        name: str | None = None,
        description: str | None = None,
    ) -> Callable[..., str]:
        """Добавление инструмента в MCP сервер.
        :param func: Функция инструмента (должна возвращать строку)
        :param name: Название инструмента (опционально)
        :param description: Описание инструмента (опционально)
        :return: Исходная функция.
        """
        tool_name = name or func.__name__
        tool_description = description or func.__doc__ or f"Инструмент {tool_name}"
        logger.info(f"Регистрация инструмента: {tool_name}")
        return self._server.tool(
            name=tool_name,
            description=tool_description,
        )(func)

    def add_resource(
        self,
        route: str,
        func: Callable[..., Awaitable[str]],
        name: str | None = None,
        description: str | None = None,
    ) -> Callable[..., str]:
        """Добавление ресурса в MCP сервер.
        :param route: Путь к ресурсу
        :param func: Функция для получения ресурса (должна возвращать строку)
        :param name: Название ресурса (опционально)
        :param description: Описание ресурса (опционально)
        :return: Исходная функция.
        """
        resource_description = description or func.__doc__ or f"Ресурс {route}"
        logger.info(f"Регистрация ресурса: {route}")
        return self._server.resource(
            route,
            name=name,
            description=resource_description,
        )(func)

    def add_prompt(
        self,
        func: Callable[..., Awaitable[str]],
        name: str | None = None,
        description: str | None = None,
    ) -> Callable[..., str]:
        """Добавление промпта в MCP сервер.
        :param func: Функция для создания промпта (должна возвращать строку)
        :param name: Название промпта (опционально)
        :param description: Описание промпта (опционально)
        :return: Исходная функция.
        """
        prompt_name = name or func.__name__
        prompt_description = description or func.__doc__ or f"Промпт {prompt_name}"
        logger.info(f"Регистрация промпта: {prompt_name}")
        return self._server.prompt(
            name=prompt_name,
            description=prompt_description,
        )(func)

    @property
    def server(self) -> FastMCP:
        """Возвращает экземпляр внутреннего MCP сервера.

        Предоставляет прямой доступ к базовому экземпляру FastMCP,
        что позволяет использовать дополнительные методы и функции,
        не обернутые в BitrixMCPServer.

        :return: Экземпляр FastMCP сервера.
        :rtype: FastMCP
        """
        return self._server
