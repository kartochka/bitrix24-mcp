"""Сервис для работы с контактами.

Предоставляет бизнес-логику для работы с контактами Bitrix24.
"""

from typing import TYPE_CHECKING, cast

from wireup import service

from src.domain.entities.contact import Contact
from src.infrastructure.bitrix.repository_factory import BitrixRepositoryFactory

if TYPE_CHECKING:
    from src.infrastructure.bitrix.bitrix_contact_repository import (
        BitrixContactRepository,
    )


@service
class ContactService:
    """Сервис для работы с контактами Bitrix24.

    Содержит методы для поиска, получения и обработки контактов.
    """

    def __init__(self, bitrix_repository_factory: BitrixRepositoryFactory):
        """Инициализация сервиса контактов.

        :param bitrix_repository_factory: Фабрика репозиториев Bitrix24
        """
        self._contact_repository: BitrixContactRepository = cast(
            'BitrixContactRepository',
            bitrix_repository_factory.get_repository('contact'),
        )

    async def get_contact_by_id(self, contact_id: int) -> Contact | None:
        """Получение контакта по идентификатору.

        :param contact_id: Идентификатор контакта
        :return: Объект контакта или None, если контакт не найден
        """
        return await self._contact_repository.get_by_id(contact_id)

    async def search_contacts(
        self,
        query: str,
        search_type: str = 'name',
        limit: int = 10,
    ) -> list[Contact]:
        """Поиск контактов по различным критериям.

        :param query: Поисковый запрос
        :param search_type: Тип поиска (name, phone, email)
        :param limit: Максимальное количество результатов
        :return: Список объектов контактов
        """
        if search_type == 'phone':
            return await self._contact_repository.search_by_phone(
                query,
                limit,
            )
        if search_type == 'email':
            return await self._contact_repository.search_by_email(
                query,
                limit,
            )
        return await self._contact_repository.search_by_name(
            query,
            limit,
        )

    async def list_contacts(
        self,
        limit: int = 50,
        company_id: int | None = None,
    ) -> list[Contact]:
        """Получение списка контактов с возможностью фильтрации.

        :param limit: Максимальное количество результатов
        :param company_id: Идентификатор компании для фильтрации (опционально)
        :return: Список объектов контактов
        """
        filter_params = {}

        if company_id:
            filter_params['COMPANY_ID'] = company_id

        return await self._contact_repository.list_entities(
            filter_params=filter_params,
            limit=limit,
        )

    async def get_deal_contacts(self, deal_id: int) -> list[Contact]:
        """Получение контактов, связанных со сделкой.

        :param deal_id: Идентификатор сделки
        :return: Список объектов контактов
        """
        return await self._contact_repository.get_deal_contacts(deal_id)

    async def create_contact(self, contact: Contact) -> int | None:
        """Создание нового контакта.

        :param contact: Объект контакта для создания
        :return: ID созданного контакта или None в случае ошибки
        """
        return await self._contact_repository.create(contact)

    async def update_contact(self, contact_id: int, contact: Contact) -> bool:
        """Обновление существующего контакта.

        :param contact_id: Идентификатор контакта
        :param contact: Объект контакта с обновленными данными
        :return: Успешность операции
        """
        return await self._contact_repository.update(contact_id, contact)

    async def update_contact_fields(
        self,
        contact_id: int,
        fields: dict[str, any],
    ) -> bool:
        """Обновление выбранных полей контакта.

        :param contact_id: Идентификатор контакта
        :param fields: Словарь с полями для обновления
        :return: Успешность операции
        """
        return await self._contact_repository.update_fields(
            contact_id,
            fields,
        )
