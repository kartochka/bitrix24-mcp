"""Модуль с реализацией репозитория для работы со сделками через API Bitrix24.

Предоставляет методы для получения, поиска, создания, обновления и удаления сделок,
а также для работы со связями между сделками и другими сущностями.
"""

from typing import Any, ClassVar

from fast_bitrix24 import Bitrix

from src.domain.entities.deal import Deal
from src.domain.interfaces.base_repository import BitrixRepository
from src.infrastructure.bitrix.bitrix_contact_repository import (
    BitrixContactRepository,
)
from src.infrastructure.logging.logger import logger

from .mixins import (
    BitrixBatchOperationsMixin,
    BitrixFilterBuilderMixin,
    BitrixPaginationMixin,
    BitrixReadMixin,
    BitrixRelationshipMixin,
    BitrixWriteMixin,
)


class BitrixDealRepository(
    BitrixReadMixin[Deal],
    BitrixWriteMixin[Deal],
    BitrixBatchOperationsMixin,
    BitrixFilterBuilderMixin,
    BitrixPaginationMixin,
    BitrixRelationshipMixin,
    BitrixRepository,
):
    """Реализация репозитория для работы со сделками через API Bitrix24.

    Предоставляет полный набор методов для взаимодействия со сделками
    в соответствии с API Bitrix24.
    """

    _entity_type: ClassVar[str] = "deal"

    _bitrix_list_method: ClassVar[str] = "crm.deal.list"
    _bitrix_get_method: ClassVar[str] = "crm.deal.get"
    _bitrix_create_method: ClassVar[str] = "crm.deal.add"
    _bitrix_update_method: ClassVar[str] = "crm.deal.update"
    _bitrix_delete_method: ClassVar[str] = "crm.deal.delete"
    _bitrix_fields_method: ClassVar[str] = "crm.deal.fields"
    _entity_factory: type[Deal] = Deal

    _deal_contact_add_method: ClassVar[str] = "crm.deal.contact.add"
    _deal_contact_delete_method: ClassVar[str] = "crm.deal.contact.delete"
    _deal_contact_items_get_method: ClassVar[str] = "crm.deal.contact.items.get"
    _deal_category_list_method: ClassVar[str] = "crm.dealcategory.list"
    _deal_category_stage_list_method: ClassVar[str] = "crm.dealcategory.stage.list"

    def __init__(
        self,
        bitrix: Bitrix,
        contact_repository: BitrixContactRepository,
    ):
        """Инициализация репозитория.

        :param bitrix: Клиент для работы с API Bitrix24
        :param contact_repository: Репозиторий для работы с контактами
        """
        super().__init__(bitrix=bitrix)

        self.contact_repository = contact_repository

    async def get_by_id(self, entity_id: int) -> Deal | None:
        """Получение сделки по её идентификатору.

        :param entity_id: Идентификатор сделки
        :return: Объект сделки или None, если сделка не найдена
        """
        error_message = f"Ошибка при получении сделки с ID={entity_id}"

        try:
            b_response: dict[str, dict[str, Any]] = await self._safe_call(
                self._bitrix.call,
                error_message,
                {},
                self._bitrix_get_method,
                {self._id_param_name: entity_id},
                raw=True,
            )
            deal_data = b_response.get("result", {})
            if not deal_data:
                return None

            contacts = await self.contact_repository.get_deal_contacts(
                entity_id,
            )
            contact_ids = [contact.id for contact in contacts]

            return self._entity_factory.from_bitrix(deal_data, contact_ids)
        except Exception as e:
            logger.error(f"{error_message}: {e}")
            return None

    async def list_entities(
        self,
        filter_params: dict[str, Any] | None = None,
        select_fields: list[str] | None = None,
        order: dict[str, str] | None = None,
        start: int = 0,
        limit: int = 50,
    ) -> list[Deal]:
        """Получение списка сделок с возможностью фильтрации.

        :param filter_params: Параметры фильтрации сделок
        :param select_fields: Список полей для выбора
        :param order: Параметры сортировки
        :param start: Начальная позиция выборки
        :param limit: Максимальное количество возвращаемых сделок
        :return: Список объектов сделок
        """
        error_message = "Ошибка при получении списка сделок"

        try:
            params: dict[str, Any] = {
                self._start_param_name: start,
            }

            if filter_params:
                params[self._filter_param_name] = filter_params

            if select_fields:
                params[self._select_param_name] = select_fields
            else:
                params[self._select_param_name] = ["*", "UF_*"]

            if order:
                params[self._order_param_name] = order
            else:
                params[self._order_param_name] = {"DATE_CREATE": "DESC"}

            b_results: dict[str, list] = await self._safe_call(
                self._bitrix.call,
                error_message,
                {},
                self._bitrix_list_method,
                items=params,
                raw=True,
            )
            results = b_results.get("result", [])

            deals = []
            for deal_data in results[:limit]:
                try:
                    deal_id = int(deal_data["ID"])

                    contacts = await self.contact_repository.get_deal_contacts(
                        deal_id,
                    )
                    contact_ids = [contact.id for contact in contacts]

                    deals.append(
                        self._entity_factory.from_bitrix(
                            deal_data,
                            contact_ids,
                        ),
                    )
                except Exception as e:
                    logger.error(
                        f'Ошибка при обработке сделки ID={deal_data.get("ID")}: {e}',
                    )
                    continue

        except Exception as e:
            logger.error(f"{error_message}: {e}")
            return []
        else:
            return deals

    async def update_stage(self, deal_id: int, stage_id: str) -> bool:
        """Обновление стадии сделки.

        :param deal_id: Идентификатор сделки
        :param stage_id: Идентификатор новой стадии
        :return: Успешность операции
        """
        return await self.update_fields(deal_id, {"STAGE_ID": stage_id})

    async def add_contact(self, deal_id: int, contact_id: int) -> bool:
        """Добавление контакта к сделке.

        :param deal_id: Идентификатор сделки
        :param contact_id: Идентификатор контакта
        :return: Успешность операции
        """
        error_message = (
            f"Ошибка при добавлении контакта ID={contact_id} к сделке ID={deal_id}"
        )

        try:
            return await self.add_relationship(
                self._deal_contact_add_method,
                deal_id,
                contact_id,
                "CONTACT_ID",
                error_message,
            )
        except Exception as e:
            logger.error(f"{error_message}: {e}")
            return False

    async def remove_contact(self, deal_id: int, contact_id: int) -> bool:
        """Удаление контакта из сделки.

        :param deal_id: Идентификатор сделки
        :param contact_id: Идентификатор контакта
        :return: Успешность операции
        """
        error_message = (
            f"Ошибка при удалении контакта ID={contact_id} из сделки ID={deal_id}"
        )

        try:
            return await self.remove_relationship(
                self._deal_contact_delete_method,
                deal_id,
                contact_id,
                "CONTACT_ID",
                error_message,
            )
        except Exception as e:
            logger.error(f"{error_message}: {e}")
            return False

    async def get_categories(self) -> dict[str, Any]:
        """Получение списка категорий сделок.

        :return: Словарь с категориями сделок
        """
        error_message = "Ошибка при получении списка категорий сделок"

        try:
            response = await self._safe_call(
                self._bitrix.call,
                error_message,
                None,
                self._deal_category_list_method,
            )

            if not response or "result" not in response:
                logger.warning(f"{error_message}: получен некорректный ответ")
                return {}

            return response.get("result", {})
        except Exception as e:
            logger.error(f"{error_message}: {e}")
            return {}

    async def get_stages(self, category_id: int = 0) -> dict[str, Any]:
        """Получение списка стадий сделок для указанной категории.

        :param category_id: Идентификатор категории
        :return: Словарь со стадиями сделок
        """
        error_message = f"Ошибка при получении стадий для категории ID={category_id}"

        try:
            response = await self._safe_call(
                self._bitrix.call,
                error_message,
                None,
                self._deal_category_stage_list_method,
                {"ID": category_id},
            )

            if not response or "result" not in response:
                logger.warning(f"{error_message}: получен некорректный ответ")
                return {}

            return response.get("result", {})
        except Exception as e:
            logger.error(f"{error_message}: {e}")
            return {}
