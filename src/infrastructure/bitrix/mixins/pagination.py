"""Модуль с миксином для пагинации при работе с API Bitrix24.

Содержит методы для получения данных с учетом пагинации API.
"""

from collections.abc import Callable
from typing import Any

from src.infrastructure.bitrix.mixins.base import BaseMixin
from src.infrastructure.logging.logger import logger


class BitrixPaginationMixin(BaseMixin):
    """Миксин для работы с пагинацией API Bitrix24.

    Предоставляет методы для эффективного получения данных
    с учетом особенностей пагинации конкретных методов API.
    """

    async def paginate[T](  # noqa: PLR0913
        self,
        method: str,
        params: dict[str, Any],
        process_page: Callable[[list[dict[str, Any]]], list[T]],
        error_message: str,
        page_size: int | None = None,
        max_items: int | None = None,
        start_param_name: str = "start",
    ) -> list[T]:
        """Получение данных с учетом пагинации.

        :param method: Метод API для вызова
        :param params: Параметры запроса
        :param process_page: Функция для обработки каждой страницы результатов
        :param error_message: Сообщение при ошибке
        :param page_size: Размер страницы (если не указан, используется максимальный)
        :param max_items: Максимальное количество элементов для получения
        :param start_param_name: Имя параметра для начальной позиции
        :returns: Объединенный список обработанных результатов
        """
        try:
            actual_page_size = page_size or 50

            all_results: list[T] = []

            current_params = params.copy()
            if start_param_name not in current_params:
                current_params[start_param_name] = 0

            total_items_to_fetch = float("inf") if max_items is None else max_items

            while len(all_results) < total_items_to_fetch:
                response = await self._bitrix.call(method, current_params)

                if not response or "result" not in response:
                    logger.warning(
                        f"{error_message}: получен некорректный ответ",
                    )
                    break

                page_items = response["result"]

                if not page_items:
                    break

                processed_items = process_page(page_items)
                all_results.extend(processed_items)

                if len(page_items) < actual_page_size:
                    break

                current_params[start_param_name] += actual_page_size

            return all_results[: int(total_items_to_fetch)]
        except Exception as e:
            logger.error(f"{error_message}: ошибка при пагинации: {e}")
            return []

    async def get_all[T](  # noqa: PLR0913
        self,
        method: str,
        params: dict[str, Any],
        processor: Callable[[dict[str, Any]], T | None],
        error_message: str,
        use_pagination: bool = True,
        page_size: int = 50,
        max_items: int | None = None,
    ) -> list[T]:
        """Получение всех элементов с использованием пагинации или без нее.

        :param method: Метод API для вызова
        :param params: Параметры запроса
        :param processor: Функция для обработки каждого элемента
        :param error_message: Сообщение при ошибке
        :param use_pagination: Использовать пагинацию
        :param page_size: Размер страницы (при использовании пагинации)
        :param max_items: Максимальное количество элементов для получения
        :returns: Список обработанных элементов
        """
        try:
            if use_pagination:
                return await self.paginate(
                    method=method,
                    params=params,
                    process_page=lambda items: [
                        processed
                        for item in items
                        if (processed := processor(item)) is not None
                    ],
                    error_message=error_message,
                    page_size=page_size,
                    max_items=max_items,
                )
            response = await self._bitrix.call(method, params)

            if not response or "result" not in response:
                logger.warning(
                    f"{error_message}: получен некорректный ответ",
                )
                return []

            items = response["result"]
            processed_items = [
                processed
                for item in items
                if (processed := processor(item)) is not None
            ]

            if max_items is not None:
                return processed_items[:max_items]
        except Exception as e:
            logger.error(f"{error_message}: {e}")
            return []
        else:
            return processed_items
