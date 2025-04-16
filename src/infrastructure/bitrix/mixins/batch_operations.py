"""Модуль с миксином для пакетных операций с API Bitrix24.

Содержит методы для эффективного выполнения множественных запросов к API.
"""

from collections.abc import Callable
from typing import Any, cast

from src.infrastructure.bitrix.mixins.base import BaseMixin
from src.infrastructure.logging.logger import logger


class BitrixBatchOperationsMixin(BaseMixin):
    """Миксин для пакетных операций с API Bitrix24.

    Предоставляет методы для эффективного выполнения
    множественных запросов к API.
    """

    async def execute_batch(
        self,
        commands: dict[str, tuple[str, dict[str, Any]]],
        error_message: str = 'Ошибка при выполнении пакетного запроса',
    ) -> dict[str, Any]:
        """Выполнение пакетного запроса.

        :param commands: Словарь команд для выполнения
        :param halt_on_error: Прерывать выполнение при ошибке
        :param error_message: Сообщение при ошибке
        :returns: Словарь результатов
        """
        try:
            batch_commands: dict[str, dict[str, Any]] = {}

            for name, (method, params) in commands.items():
                batch_commands[name] = {
                    'method': method,
                    'params': params,
                }

            response = await self._bitrix.call_batch(batch_commands)

            if not response or 'result' not in response:
                logger.warning(f'{error_message}: получен некорректный ответ')
                return {}

            return response['result'] or {}
        except ValueError as e:
            logger.error(f'{error_message}: некорректное значение: {e}')
            return {}
        except KeyError as e:
            logger.error(f'{error_message}: отсутствует ключ: {e}')
            return {}
        except AttributeError as e:
            logger.error(f'{error_message}: ошибка атрибута: {e}')
            return {}
        except Exception as e:
            logger.error(f'{error_message}: {e}')
            return {}

    async def batch_list(
        self,
        method: str,
        params: dict[str, Any],
        error_message: str = 'Ошибка при выполнении пакетного запроса списка',
    ) -> list[dict[str, Any]]:
        """Получение списка элементов пакетными запросами.

        :param method: Метод API для получения списка
        :param params: Параметры запроса
        :param batch_size: Размер пакета
        :param error_message: Сообщение при ошибке
        :returns: Список результатов
        """
        try:
            result = await self._bitrix.get_all(
                method=method,
                params=params,
            )
            return cast('list[dict[str, Any]]', result) or []
        except Exception as e:
            logger.error(f'{error_message} через {method}: {e}')
            return []

    async def batch_get_by_ids[T](
        self,
        method: str,
        entity_ids: list[int],
        processor: Callable[[dict[str, Any]], T | None],
        error_message: str = 'Ошибка при пакетном получении по идентификаторам',
    ) -> dict[int, T]:
        """Пакетное получение сущностей по идентификаторам.

        :param method: Метод API для получения сущности
        :param entity_ids: Список идентификаторов
        :param processor: Функция для обработки результатов
        :param error_message: Сообщение при ошибке
        :returns: Словарь сущностей по идентификаторам
        """
        if not entity_ids:
            return {}

        try:
            commands: dict[str, tuple[str, dict[str, Any]]] = {}

            for i, entity_id in enumerate(entity_ids):
                commands[f'cmd{i}'] = (method, {'ID': entity_id})

            results = await self.execute_batch(
                commands,
                error_message=error_message,
            )

            entities: dict[int, T] = {}

            for i, entity_id in enumerate(entity_ids):
                result = results.get(f'cmd{i}')
                if result:
                    entity = processor(result)
                    if entity:
                        entities[entity_id] = entity

        except Exception as e:
            logger.error(f'{error_message}: {e}')
            return {}
        else:
            return entities

    async def batch_create(
        self,
        method: str,
        items: list[dict[str, Any]],
        error_message: str = 'Ошибка при пакетном создании',
    ) -> list[int | None]:
        """Пакетное создание элементов.

        :param method: Метод API для создания элементов
        :param items: Список элементов для создания
        :param error_message: Сообщение при ошибке
        :returns: Список ID созданных элементов (или None при ошибке)
        """
        if not items:
            return []

        try:
            commands: dict[str, tuple[str, dict[str, Any]]] = {}

            for i, item in enumerate(items):
                commands[f'cmd{i}'] = (method, item)

            results = await self.execute_batch(
                commands,
                error_message=error_message,
            )

            ids: list[int | None] = []
            for i in range(len(items)):
                cmd_key = f'cmd{i}'
                if results.get(cmd_key):
                    try:
                        ids.append(int(results[cmd_key]))
                    except (ValueError, TypeError):
                        logger.error(
                            f'Не удалось преобразовать ID={results[cmd_key]} '
                            'к целому числу',
                        )
                        ids.append(None)
                else:
                    ids.append(None)

        except Exception as e:
            logger.error(f'{error_message} через {method}: {e}')
            return [None] * len(items)
        else:
            return ids
