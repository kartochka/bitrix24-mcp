"""Модуль с базовым миксином для обработки ошибок.

Содержит общие методы для безопасного выполнения асинхронных операций
с обработкой исключений и логированием.
"""

import typing
from collections.abc import Awaitable, Callable

from fast_bitrix24 import Bitrix

from src.domain.entities.base_entity import BitrixEntity
from src.infrastructure.logging.logger import logger


class BaseMixin[T_Result]:
    """Базовый миксин для обработки ошибок при выполнении асинхронных операций.

    Предоставляет методы для безопасного выполнения асинхронных функций
    с логированием и обработкой распространенных исключений.
    """

    def __init__(self, bitrix: Bitrix):
        """Инициализация миксина.

        :param bitrix: Клиент для работы с API Bitrix24
        """
        self._bitrix = bitrix

    @classmethod
    async def _safe_call(  # noqa: PLR0911
        cls,
        func: Callable[..., Awaitable[T_Result]],
        error_context_message: str,
        default_value: T_Result,
        *args: typing.Any,
        **kwargs: typing.Any,
    ) -> T_Result:
        """Безопасно выполняет асинхронную функцию с обработкой ошибок.

        Логирует возникшие исключения и возвращает значение по умолчанию
        в случае ошибки.

        :param func: Асинхронная функция для выполнения.
        :param error_context_message: Контекстное сообщение для лога ошибки
        :param default_value: Значение, которое будет возвращено при возникновении
                              любого из отлавливаемых исключений.
        :param args: Позиционные аргументы для передачи в `func`.
        :param kwargs: Именованные аргументы для передачи в `func`.
        :returns: Результат выполнения `func` в случае успеха, иначе `default_value`.
        """
        try:
            return await func(*args, **kwargs)
        except ConnectionError:
            logger.error(f'{error_context_message}: Ошибка соединения.')
            return default_value
        except TimeoutError:
            logger.error(
                f'{error_context_message}: Превышено время ожидания ответа.',
            )
            return default_value
        except ValueError as e:
            logger.error(f'{error_context_message}: Некорректное значение: {e}')
            return default_value
        except KeyError as e:
            logger.error(
                f'{error_context_message}: Отсутствует ожидаемый ключ: {e}',
            )
            return default_value
        except TypeError as e:
            logger.error(f'{error_context_message}: Ошибка типа: {e}')
            return default_value
        except AttributeError as e:
            logger.error(
                f'{error_context_message}: Ошибка доступа к атрибуту: {e}',
            )
            return default_value
        except RuntimeError as e:
            logger.error(f'{error_context_message}: Ошибка выполнения: {e}')
            return default_value
        except Exception as e:
            logger.exception(
                f'{error_context_message}: Неожиданная ошибка: {e}',
                exc_info=True,
            )
            return default_value

    @staticmethod
    def _format_entity_name(entity_class: type[BitrixEntity]) -> str:
        """Форматирование имени сущности для логирования.

        :param entity_class: Класс сущности
        :returns: Отформатированное имя сущности
        """
        if hasattr(entity_class, '__name__'):
            return entity_class.__name__
        return str(entity_class)
