"""Модуль с реализацией репозитория для работы с контактами через API Bitrix24.

Предоставляет методы для получения, поиска, создания, обновления и удаления контактов,
а также для работы со связями между контактами и другими сущностями.
"""

from typing import Any, ClassVar

from fast_bitrix24 import Bitrix

from src.domain.entities.contact import Contact
from src.domain.interfaces.base_repository import BitrixRepository
from src.infrastructure.logging.logger import logger

from .mixins import (
    BitrixBatchOperationsMixin,
    BitrixFilterBuilderMixin,
    BitrixPaginationMixin,
    BitrixReadMixin,
    BitrixRelationshipMixin,
    BitrixWriteMixin,
)


class BitrixContactRepository(
    BitrixReadMixin[Contact],
    BitrixWriteMixin[Contact],
    BitrixBatchOperationsMixin,
    BitrixFilterBuilderMixin,
    BitrixPaginationMixin,
    BitrixRelationshipMixin,
    BitrixRepository,
):
    """Реализация репозитория для работы с контактами через API Bitrix24.

    Предоставляет полный набор методов для взаимодействия с контактами
    в соответствии с API Bitrix24.
    """

    _entity_type: ClassVar[str] = "contact"

    _bitrix_list_method: ClassVar[str] = "crm.contact.list"
    _bitrix_get_method: ClassVar[str] = "crm.contact.get"
    _bitrix_create_method: ClassVar[str] = "crm.contact.add"
    _bitrix_update_method: ClassVar[str] = "crm.contact.update"
    _bitrix_delete_method: ClassVar[str] = "crm.contact.delete"
    _bitrix_fields_method: ClassVar[str] = "crm.contact.fields"
    _entity_factory: type[Contact] = Contact

    _company_items_method: ClassVar[str] = "crm.contact.company.items.get"

    def __init__(self, bitrix: Bitrix):
        """Инициализация репозитория.

        :param bitrix: Клиент для работы с API Bitrix24
        """
        super().__init__(bitrix=bitrix)

    async def search_by_name(self, name: str, limit: int = 10) -> list[Contact]:
        """Поиск контактов по имени.

        :param name: Строка для поиска
        :param limit: Максимальное количество результатов
        :return: Список объектов контактов
        """
        error_message = f"Ошибка при поиске контактов по имени '{name}'"

        try:
            filter_params = {
                "$SEARCH": name,
                "CHECK_PERMISSIONS": "N",
            }

            return await self.list_entities(
                filter_params=filter_params,
                limit=limit,
            )
        except Exception as e:
            logger.error(f"{error_message}: {e}")
            return []

    async def search_by_phone(
        self,
        phone: str,
        limit: int = 10,
    ) -> list[Contact]:
        """Поиск контактов по номеру телефона.

        :param phone: Номер телефона для поиска
        :param limit: Максимальное количество результатов
        :return: Список объектов контактов
        """
        error_message = f"Ошибка при поиске контактов по телефону '{phone}'"

        try:
            filter_params = {
                "PHONE": phone,
                "CHECK_PERMISSIONS": "N",
            }

            return await self.list_entities(
                filter_params=filter_params,
                limit=limit,
            )
        except Exception as e:
            logger.error(f"{error_message}: {e}")
            return []

    async def search_by_email(
        self,
        email: str,
        limit: int = 10,
    ) -> list[Contact]:
        """Поиск контактов по email.

        :param email: Email для поиска
        :param limit: Максимальное количество результатов
        :return: Список объектов контактов
        """
        error_message = f"Ошибка при поиске контактов по email '{email}'"

        try:
            filter_params = {
                "EMAIL": email,
                "CHECK_PERMISSIONS": "N",
            }

            return await self.list_entities(
                filter_params=filter_params,
                limit=limit,
            )
        except Exception as e:
            logger.error(f"{error_message}: {e}")
            return []

    async def get_deal_contacts(self, deal_id: int) -> list[Contact]:
        """Получение контактов, связанных со сделкой.

        :param deal_id: Идентификатор сделки
        :return: Список объектов контактов
        """
        error_message = f"Ошибка при получении контактов сделки ID={deal_id}"

        try:
            contacts_result = await self.get_related_items(
                "crm.deal.contact.items.get",
                deal_id,
                error_message,
            )

            if not contacts_result:
                return []

            contact_ids = [int(contact["CONTACT_ID"]) for contact in contacts_result]

            return await self._load_contacts_by_ids(contact_ids)
        except Exception as e:
            logger.error(f"{error_message}: {e}")
            return []

    async def _load_contacts_by_ids(
        self,
        contact_ids: list[int],
    ) -> list[Contact]:
        """Загрузка контактов по списку идентификаторов.

        :param contact_ids: Список идентификаторов контактов
        :return: Список объектов контактов
        """
        if not contact_ids:
            return []

        error_message = f"Ошибка при загрузке контактов по ID: {contact_ids}"

        try:
            filter_params = {
                "ID": contact_ids,
                "CHECK_PERMISSIONS": "N",
            }

            return await self.list_entities(
                filter_params=filter_params,
                limit=len(contact_ids),
            )
        except Exception as e:
            logger.error(f"{error_message}: {e}")
            return []

    async def get_contact_companies(
        self,
        contact_id: int,
    ) -> list[dict[str, Any]]:
        """Получение компаний, связанных с контактом.

        :param contact_id: Идентификатор контакта
        :return: Список данных о компаниях
        """
        error_message = f"Ошибка при получении компаний контакта ID={contact_id}"

        try:
            return await self.get_related_items(
                self._company_items_method,
                contact_id,
                error_message,
            )
        except Exception as e:
            logger.error(f"{error_message}: {e}")
            return []
