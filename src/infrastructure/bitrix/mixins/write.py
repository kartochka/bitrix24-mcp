"""Модуль с миксином для операций записи в Bitrix24 API.

Содержит методы для создания, обновления и удаления данных в API Bitrix24.
"""

from typing import Any, ClassVar

from src.domain.entities.base_entity import BitrixEntity
from src.infrastructure.bitrix.mixins.base import BaseMixin
from src.infrastructure.logging.logger import logger


class BitrixWriteMixin[T: BitrixEntity](BaseMixin):
    """Миксин для операций записи данных в Bitrix24 API.

    Предоставляет методы для создания, обновления и удаления сущностей.
    """

    _bitrix_create_method: ClassVar[str]
    _bitrix_update_method: ClassVar[str]
    _bitrix_delete_method: ClassVar[str]
    _entity_factory: type[T]

    _id_param_name: ClassVar[str] = 'ID'
    _fields_param_name: ClassVar[str] = 'fields'

    async def create(self, entity: T) -> int | None:
        """Создание новой сущности.

        :param entity: Объект сущности для создания
        :return: ID созданной сущности или None в случае ошибки
        """
        error_message = (
            f'Ошибка при создании сущности '
            f'{self._format_entity_name(self._entity_factory)}'
        )

        try:
            fields = entity.to_bitrix()

            response = await self._safe_call(
                self._bitrix.call,
                error_message,
                None,
                self._bitrix_create_method,
                {self._fields_param_name: fields},
            )

            if not response or 'result' not in response:
                logger.warning(f'{error_message}: получен некорректный ответ')
                return None

            result = response.get('result')
            if not result:
                logger.error(
                    f'{error_message}: отсутствует идентификатор в ответе',
                )
                return None

            try:
                return int(result)
            except (ValueError, TypeError):
                logger.error(
                    f'Не удалось преобразовать ID={result} к целому числу '
                    f'при создании сущности '
                    f'{self._format_entity_name(self._entity_factory)}',
                )
                return None
        except Exception as e:
            logger.error(f'{error_message}: {e}')
            return None

    async def update(self, entity_id: int, entity: T) -> bool:
        """Обновление существующей сущности.

        :param entity_id: Идентификатор сущности
        :param entity: Объект сущности с обновленными данными
        :return: True, если обновление успешно, иначе False
        """
        error_message = (
            f'Ошибка при обновлении сущности '
            f'{self._format_entity_name(self._entity_factory)} с ID={entity_id}'
        )

        try:
            fields = entity.to_bitrix()

            response = await self._safe_call(
                self._bitrix.call,
                error_message,
                None,
                self._bitrix_update_method,
                {
                    self._id_param_name: entity_id,
                    self._fields_param_name: fields,
                },
            )

            if not response or 'result' not in response:
                logger.warning(f'{error_message}: получен некорректный ответ')
                return False

            return bool(response.get('result'))
        except Exception as e:
            logger.error(f'{error_message}: {e}')
            return False

    async def update_fields(
        self,
        entity_id: int,
        fields: dict[str, Any],
    ) -> bool:
        """Обновление выбранных полей существующей сущности.

        :param entity_id: Идентификатор сущности
        :param fields: Словарь с полями для обновления
        :return: True, если обновление успешно, иначе False
        """
        error_message = (
            f'Ошибка при обновлении полей сущности '
            f'{self._format_entity_name(self._entity_factory)} с ID={entity_id}'
        )

        try:
            response = await self._safe_call(
                self._bitrix.call,
                error_message,
                None,
                self._bitrix_update_method,
                {
                    self._id_param_name: entity_id,
                    self._fields_param_name: fields,
                },
            )

            if not response or 'result' not in response:
                logger.warning(f'{error_message}: получен некорректный ответ')
                return False

            return bool(response.get('result'))
        except Exception as e:
            logger.error(f'{error_message}: {e}')
            return False

    async def delete(self, entity_id: int) -> bool:
        """Удаление сущности.

        :param entity_id: Идентификатор сущности
        :return: True, если удаление успешно, иначе False
        """
        error_message = (
            f'Ошибка при удалении сущности '
            f'{self._format_entity_name(self._entity_factory)} с ID={entity_id}'
        )

        try:
            response = await self._safe_call(
                self._bitrix.call,
                error_message,
                None,
                self._bitrix_delete_method,
                {self._id_param_name: entity_id},
            )

            if not response or 'result' not in response:
                logger.warning(f'{error_message}: получен некорректный ответ')
                return False

            return bool(response.get('result'))
        except Exception as e:
            logger.error(f'{error_message}: {e}')
            return False
