"""Сервис для работы со сделками.

Предоставляет бизнес-логику для работы со сделками Bitrix24.
"""

from typing import TYPE_CHECKING, Any, cast

from wireup import service

from src.domain.entities.deal import Deal
from src.infrastructure.bitrix.repository_factory import BitrixRepositoryFactory

if TYPE_CHECKING:
    from src.infrastructure.bitrix.bitrix_contact_repository import (
        BitrixContactRepository,
    )
    from src.infrastructure.bitrix.bitrix_deal_repository import (
        BitrixDealRepository,
    )


@service
class DealService:
    """Сервис для работы со сделками Bitrix24.

    Содержит методы для поиска, получения и обработки сделок.
    """

    def __init__(self, bitrix_repository_factory: BitrixRepositoryFactory):
        """Инициализация сервиса сделок.

        :param bitrix_repository_factory: Фабрика репозиториев Bitrix24
        """
        self._deal_repository: BitrixDealRepository = cast(
            'BitrixDealRepository',
            bitrix_repository_factory.get_repository('deal'),
        )

        self._contact_repository: BitrixContactRepository = cast(
            'BitrixContactRepository',
            bitrix_repository_factory.get_repository('contact'),
        )

    async def get_deal_by_id(self, deal_id: int) -> Deal | None:
        """Получение сделки по идентификатору.

        :param deal_id: Идентификатор сделки
        :return: Объект сделки или None, если сделка не найдена
        """
        return await self._deal_repository.get_by_id(deal_id)

    async def list_deals(
        self,
        active_only: bool = False,
        contact_id: int | None = None,
        company_id: int | None = None,
        limit: int = 50,
    ) -> list[Deal]:
        """Получение списка сделок с возможностью фильтрации.

        :param active_only: Только активные сделки
        :param contact_id: Идентификатор контакта для фильтрации (опционально)
        :param company_id: Идентификатор компании для фильтрации (опционально)
        :param limit: Максимальное количество результатов
        :return: Список объектов сделок
        """
        filter_params: dict[str, Any] = {}

        if active_only:
            filter_params['STAGE_ID'] = [
                'C14:NEW',
                'C14:PREPARATION',
                'C14:EXECUTING',
            ]

        if contact_id:
            filter_params['CONTACT_ID'] = contact_id

        if company_id:
            filter_params['COMPANY_ID'] = company_id

        return await self._deal_repository.list_entities(
            filter_params=filter_params,
            order={'DATE_CREATE': 'DESC'},
            limit=limit,
        )

    async def update_deal_stage(self, deal_id: int, stage_id: str) -> bool:
        """Обновление стадии сделки.

        :param deal_id: Идентификатор сделки
        :param stage_id: Идентификатор новой стадии
        :return: True, если обновление успешно, иначе False
        """
        return await self._deal_repository.update_stage(deal_id, stage_id)

    async def add_contact_to_deal(self, deal_id: int, contact_id: int) -> bool:
        """Добавление контакта к сделке.

        :param deal_id: Идентификатор сделки
        :param contact_id: Идентификатор контакта
        :return: True, если операция успешна, иначе False
        """
        return await self._deal_repository.add_contact(deal_id, contact_id)

    async def remove_contact_from_deal(
        self,
        deal_id: int,
        contact_id: int,
    ) -> bool:
        """Удаление контакта из сделки.

        :param deal_id: Идентификатор сделки
        :param contact_id: Идентификатор контакта
        :return: True, если операция успешна, иначе False
        """
        return await self._deal_repository.remove_contact(
            deal_id,
            contact_id,
        )

    async def create_deal(self, deal: Deal) -> int | None:
        """Создание новой сделки.

        :param deal: Объект сделки для создания
        :return: ID созданной сделки или None в случае ошибки
        """
        return await self._deal_repository.create(deal)

    async def update_deal(self, deal_id: int, deal: Deal) -> bool:
        """Обновление существующей сделки.

        :param deal_id: Идентификатор сделки
        :param deal: Объект сделки с обновленными данными
        :return: Успешность операции
        """
        return await self._deal_repository.update(deal_id, deal)

    async def get_deal_stages(self, category_id: int = 0) -> dict[str, Any]:
        """Получение списка стадий сделок для указанной категории.

        :param category_id: Идентификатор категории
        :return: Словарь со стадиями сделок
        """
        return await self._deal_repository.get_stages(category_id)
