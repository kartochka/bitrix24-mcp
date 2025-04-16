"""Модуль с миксином для построения фильтров запросов к API Bitrix24.

Содержит методы для создания и комбинирования фильтров в соответствии
с документацией API Bitrix24.
"""

from typing import Any

from src.infrastructure.bitrix.mixins.base import BaseMixin


class BitrixFilterBuilderMixin(BaseMixin):
    """Миксин для построения фильтров запросов к API Bitrix24.

    Предоставляет методы для создания сложных фильтров в соответствии
    с документацией API Bitrix24.
    """

    @staticmethod
    def build_filter(
        filter_params: dict[str, Any] | None = None,
        filter_logic: dict[str, dict[str, Any]] | None = None,
    ) -> dict[str, Any]:
        """Построение фильтра для запроса к API Bitrix24.

        :param filter_params: Базовые параметры фильтра
        :param filter_logic: Параметры логики фильтрации с операторами
        :returns: Построенный фильтр для запроса
        """
        result_filter: dict[str, Any] = {}

        if filter_params:
            result_filter.update(filter_params)

        if filter_logic:
            for field, operators in filter_logic.items():
                for operator, value in operators.items():
                    filter_key = f'{operator}{field}'
                    result_filter[filter_key] = value

        return result_filter

    @staticmethod
    def add_search_filter(
        field: str,
        query: str,
        exact_match: bool = False,
    ) -> dict[str, Any]:
        """Создание фильтра для поиска по подстроке.

        :param field: Поле для поиска
        :param query: Поисковый запрос
        :param exact_match: Точное совпадение
        :returns: Фильтр для поиска
        """
        if exact_match:
            return {field: query}
        return {f'%{field}': query}

    @staticmethod
    def add_range_filter(
        field: str,
        min_value: float | None = None,
        max_value: float | None = None,
    ) -> dict[str, Any]:
        """Создание фильтра для диапазона значений.

        :param field: Поле для фильтрации
        :param min_value: Минимальное значение
        :param max_value: Максимальное значение
        :returns: Фильтр для диапазона
        """
        result = {}
        if min_value is not None:
            result[f'>={field}'] = min_value
        if max_value is not None:
            result[f'<={field}'] = max_value
        return result

    @staticmethod
    def add_in_filter(
        field: str,
        values: list[Any],
        exclude: bool = False,
    ) -> dict[str, Any]:
        """Создание фильтра для списка значений (IN или NOT IN).

        :param field: Поле для фильтрации
        :param values: Список значений
        :param exclude: Исключить значения (NOT IN)
        :returns: Фильтр для списка значений
        """
        operator = '!@' if exclude else '@'
        return {f'{operator}{field}': values}
