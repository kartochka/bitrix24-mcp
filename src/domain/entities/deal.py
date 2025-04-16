"""Модуль с сущностью сделки Bitrix24.

Содержит доменную модель сделки со всеми необходимыми атрибутами.
"""

from dataclasses import dataclass, field
from typing import Any, ClassVar, Self

from src.domain.bitrix_types import (
    BitrixCategoryID,
    BitrixCurrencyID,
    BitrixDateTime,
    BitrixID,
    BitrixStageID,
)
from src.domain.entities.base_entity import BitrixEntity


@dataclass
class Deal(BitrixEntity):
    """Сущность сделки в CRM Bitrix24.

    Представляет доменную модель сделки со всеми необходимыми атрибутами.
    """

    title: str = ''
    stage_id: BitrixStageID = ''
    company_id: BitrixID | None = None
    opportunity: float = 0.0
    currency_id: BitrixCurrencyID = ''
    assigned_by_id: BitrixID | None = None
    created_by_id: BitrixID | None = None
    modified_by_id: BitrixID | None = None
    date_create: BitrixDateTime | None = None
    date_modify: BitrixDateTime | None = None
    contact_ids: list[BitrixID] = field(default_factory=list)
    category_id: BitrixCategoryID = 0

    _bitrix_field_mapping: ClassVar[dict[str, str]] = {
        'ID': 'id',
        'TITLE': 'title',
        'STAGE_ID': 'stage_id',
        'COMPANY_ID': 'company_id',
        'OPPORTUNITY': 'opportunity',
        'CURRENCY_ID': 'currency_id',
        'ASSIGNED_BY_ID': 'assigned_by_id',
        'CREATED_BY_ID': 'created_by_id',
        'MODIFY_BY_ID': 'modified_by_id',
        'DATE_CREATE': 'date_create',
        'DATE_MODIFY': 'date_modify',
        'CATEGORY_ID': 'category_id',
    }

    @classmethod
    def from_bitrix(
        cls,
        data: dict[str, Any],
        contact_ids: list[int] | None = None,
    ) -> Self:
        """Создание сделки из данных Bitrix24.

        :param data: Словарь с данными из API Bitrix24
        :param contact_ids: Список идентификаторов контактов
        :return: Объект сделки
        """
        deal = super().from_bitrix(data)

        if contact_ids is not None:
            deal.contact_ids = contact_ids

        deal._convert_types()  # noqa: SLF001

        return deal

    def _convert_types(self) -> None:
        """Преобразование строковых значений в соответствующие типы.

        API Битрикса возвращает все в виде строк,
        поэтому нужно провести корректное преобразование.
        """
        if isinstance(self.id, str) and self.id.isdigit():
            self.id = int(self.id)

        if isinstance(self.company_id, str):
            if self.company_id.isdigit():
                self.company_id = int(self.company_id)
            else:
                self.company_id = None

        if isinstance(self.opportunity, str):
            try:
                self.opportunity = float(self.opportunity)
            except ValueError:
                self.opportunity = 0.0

        if isinstance(self.assigned_by_id, str) and self.assigned_by_id.isdigit():
            self.assigned_by_id = int(self.assigned_by_id)

        if isinstance(self.created_by_id, str) and self.created_by_id.isdigit():
            self.created_by_id = int(self.created_by_id)

        if isinstance(self.modified_by_id, str) and self.modified_by_id.isdigit():
            self.modified_by_id = int(self.modified_by_id)

        if isinstance(self.category_id, str) and self.category_id.isdigit():
            self.category_id = int(self.category_id)

        if isinstance(self.contact_ids, str):
            self.contact_ids = [
                int(iid) for iid in self.contact_ids.split(',') if iid.isdigit()
            ]

    def is_active(self) -> bool:
        """Проверка, является ли сделка активной.

        :return: True, если сделка активна, иначе False
        """
        final_stages = ['C14:LOSE', 'C14:WON']
        return self.stage_id not in final_stages
