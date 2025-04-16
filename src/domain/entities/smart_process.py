"""Модуль с сущностью смарт-процесса Bitrix24.

Содержит доменную модель смарт-процесса со всеми необходимыми атрибутами.
"""

from dataclasses import dataclass, field
from typing import Any, ClassVar, Self

from src.domain.bitrix_types import BitrixDateTime, BitrixID, BitrixStageID
from src.domain.entities.base_entity import BitrixEntity


@dataclass
class SmartProcess(BitrixEntity):
    """Сущность смарт-процесса в CRM Bitrix24.

    Представляет доменную модель смарт-процесса со всеми необходимыми атрибутами.
    """

    type_id: int = 0
    title: str = ""
    stage_id: BitrixStageID = ""
    company_id: BitrixID | None = None
    assigned_by_id: BitrixID | None = None
    created_by_id: BitrixID | None = None
    modified_by_id: BitrixID | None = None
    date_create: BitrixDateTime | None = None
    date_modify: BitrixDateTime | None = None
    contact_ids: list[BitrixID] = field(default_factory=list)

    # Расширенный маппинг полей Bitrix24 для смарт-процесса
    _bitrix_field_mapping: ClassVar[dict[str, str]] = {
        "ID": "id",
        "TITLE": "title",
        "STAGE_ID": "stage_id",
        "COMPANY_ID": "company_id",
        "ASSIGNED_BY_ID": "assigned_by_id",
        "CREATED_BY_ID": "created_by_id",
        "MODIFY_BY_ID": "modified_by_id",
        "DATE_CREATE": "date_create",
        "DATE_MODIFY": "date_modify",
        "TYPE_ID": "type_id",
    }

    @classmethod
    def from_bitrix(
        cls,
        data: dict[str, Any],
        contact_ids: list[int] | None = None,
    ) -> Self:
        """Создание смарт-процесса из данных Bitrix24.

        :param data: Словарь с данными из API Bitrix24
        :param contact_ids: Список идентификаторов контактов
        :return: Объект смарт-процесса
        """
        smart_process = super().from_bitrix(data)

        if contact_ids is not None:
            smart_process.contact_ids = contact_ids

        smart_process._convert_types()  # noqa: SLF001

        return smart_process

    def _convert_types(self) -> None:
        """Преобразование строковых значений в соответствующие типы.

        API Битрикса возвращает все в виде строк,
        поэтому нужно провести корректное преобразование.
        """
        if isinstance(self.id, str) and self.id.isdigit():
            self.id = int(self.id)

        if isinstance(self.type_id, str) and self.type_id.isdigit():
            self.type_id = int(self.type_id)

        if isinstance(self.company_id, str):
            if self.company_id.isdigit():
                self.company_id = int(self.company_id)
            else:
                self.company_id = None

        if isinstance(self.assigned_by_id, str) and self.assigned_by_id.isdigit():
            self.assigned_by_id = int(self.assigned_by_id)

        if isinstance(self.created_by_id, str) and self.created_by_id.isdigit():
            self.created_by_id = int(self.created_by_id)

        if isinstance(self.modified_by_id, str) and self.modified_by_id.isdigit():
            self.modified_by_id = int(self.modified_by_id)

        if isinstance(self.contact_ids, str):
            self.contact_ids = [
                int(iid) for iid in self.contact_ids.split(",") if iid.isdigit()
            ]

    def is_active(self) -> bool:
        """Проверка, является ли смарт-процесс активным.

        :return: True, если смарт-процесс активен, иначе False
        """
        return True

    def get_element_type(self) -> str:
        """Получение типа элемента для API запросов.

        :return: Строка с типом элемента для API
        """
        return f"DYNAMIC_{self.type_id}"
