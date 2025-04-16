"""Модуль с миксином для операций чтения из Bitrix24 API.

Содержит методы для получения данных из API Bitrix24 с учетом
особенностей разных типов сущностей.
"""

from typing import Any, ClassVar

from src.domain.entities.base_entity import BitrixEntity
from src.infrastructure.bitrix.mixins.base import BaseMixin
from src.infrastructure.logging.logger import logger


class BitrixReadMixin[T: BitrixEntity](BaseMixin):
    """Миксин для операций чтения данных из Bitrix24 API.

    Предоставляет методы для получения сущностей и их списков.
    """

    _bitrix_list_method: ClassVar[str]
    _bitrix_get_method: ClassVar[str]
    _bitrix_fields_method: ClassVar[str]
    _entity_factory: type[T]

    _id_param_name: ClassVar[str] = 'ID'
    _filter_param_name: ClassVar[str] = 'filter'
    _select_param_name: ClassVar[str] = 'select'
    _order_param_name: ClassVar[str] = 'order'
    _start_param_name: ClassVar[str] = 'start'

    async def get_by_id(self, entity_id: int) -> T | None:
        """Получение сущности по идентификатору.

        :param entity_id: Идентификатор сущности
        :return: Объект сущности или None, если сущность не найдена
        """
        error_message = (
            f'Ошибка при получении {self._format_entity_name(self._entity_factory)} '
            f'с ID={entity_id}'
        )

        try:
            response = await self._safe_call(
                self._bitrix.call,
                error_message,
                None,
                self._bitrix_get_method,
                {self._id_param_name: entity_id},
                raw=True,
            )

            if not response or 'result' not in response:
                logger.warning(f'{error_message}: получен некорректный ответ')
                return None

            result = response.get('result')
            if not result:
                return None

            return await self._process_entity(result)
        except Exception as e:
            logger.error(f'{error_message}: {e}')
            return None

    async def list_entities(
        self,
        filter_params: dict[str, Any] | None = None,
        select_fields: list[str] | None = None,
        order: dict[str, str] | None = None,
        start: int = 0,
        limit: int = 50,
    ) -> list[T]:
        """Получение списка сущностей с возможностью фильтрации.

        :param filter_params: Параметры фильтрации
        :param select_fields: Список полей для выбора
        :param order: Параметры сортировки
        :param start: Начальная позиция выборки
        :param limit: Максимальное количество возвращаемых записей
        :return: Список сущностей
        """
        error_message = (
            f'Ошибка при получении списка сущностей '
            f'{self._format_entity_name(self._entity_factory)}'
        )

        try:
            params: dict[str, Any] = {
                self._start_param_name: start,
            }

            if filter_params:
                params[self._filter_param_name] = filter_params

            if select_fields:
                params[self._select_param_name] = select_fields
            else:
                params[self._select_param_name] = ['*', 'UF_*']

            if order:
                params[self._order_param_name] = order

            b_results: dict[str, list[dict[str, Any]]] = await self._safe_call(
                self._bitrix.call,
                error_message,
                {},
                self._bitrix_list_method,
                items=params,
                raw=True,
            )
            results = b_results.get('result', [])[:limit]

            results = results[:limit]

            entities: list[T] = []

            for result in results:
                entity = await self._process_entity(result)
                if entity:
                    entities.append(entity)

        except Exception as e:
            logger.error(f'{error_message}: {e}')
            return []
        else:
            return entities

    async def get_fields(self) -> dict[str, Any]:
        """Получение описания полей сущности.

        :return: Словарь с описанием полей сущности
        """
        error_message = (
            f'Ошибка при получении описания полей сущности '
            f'{self._format_entity_name(self._entity_factory)}'
        )

        response = await self._safe_call(
            self._bitrix.call,
            error_message,
            None,
            self._bitrix_fields_method,
        )

        if not response or 'result' not in response:
            logger.warning(f'{error_message}: получен некорректный ответ')
            return {}

        return response.get('result', {})

    async def _process_entity(self, data: dict[str, Any]) -> T | None:
        """Обработка данных сущности из API.

        Метод для переопределения в дочерних классах для
        добавления дополнительной логики обработки.

        :param data: Данные сущности из API
        :return: Объект сущности или None
        """
        try:
            return self._entity_factory.from_bitrix(data)
        except Exception as e:
            entity_id = data.get('ID', 'неизвестный ID')
            logger.error(
                f'Ошибка при обработке сущности '
                f'{self._format_entity_name(self._entity_factory)} '
                f'с ID={entity_id}: {e}',
            )
            return None
