"""Модуль с сущностью контакта Bitrix24.

Содержит доменную модель контакта со всеми необходимыми атрибутами.
"""

from dataclasses import dataclass, field
from typing import Any, ClassVar, Self

from src.domain.bitrix_types import BitrixDateTime, BitrixID, BitrixMultiField
from src.domain.entities.base_entity import BitrixEntity


@dataclass
class Contact(BitrixEntity):
    """Сущность контакта в CRM Bitrix24.

    Представляет доменную модель контакта со всеми необходимыми атрибутами.
    """

    name: str = ''
    last_name: str = ''
    second_name: str = ''
    email: list[BitrixMultiField] = field(default_factory=list)
    phone: list[BitrixMultiField] = field(default_factory=list)
    company_id: BitrixID | None = None
    assigned_by_id: BitrixID | None = None
    created_by_id: BitrixID | None = None
    modified_by_id: BitrixID | None = None
    date_create: BitrixDateTime | None = None
    date_modify: BitrixDateTime | None = None

    _bitrix_field_mapping: ClassVar[dict[str, str]] = {
        'ID': 'id',
        'NAME': 'name',
        'LAST_NAME': 'last_name',
        'SECOND_NAME': 'second_name',
        'COMPANY_ID': 'company_id',
        'ASSIGNED_BY_ID': 'assigned_by_id',
        'CREATED_BY_ID': 'created_by_id',
        'MODIFY_BY_ID': 'modified_by_id',
        'DATE_CREATE': 'date_create',
        'DATE_MODIFY': 'date_modify',
    }

    @classmethod
    def from_bitrix(cls, data: dict[str, Any]) -> Self:
        """Создание контакта из данных Bitrix24.

        :param data: Словарь с данными из API Bitrix24
        :return: Объект контакта
        """
        contact = super().from_bitrix(data)

        if 'EMAIL' in data:
            contact.email = [
                BitrixMultiField.from_bitrix(email_data) for email_data in data['EMAIL']
            ]

        if 'PHONE' in data:
            contact.phone = [
                BitrixMultiField.from_bitrix(phone_data) for phone_data in data['PHONE']
            ]

        contact._convert_types()  # noqa: SLF001

        return contact

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

        if isinstance(self.assigned_by_id, str) and self.assigned_by_id.isdigit():
            self.assigned_by_id = int(self.assigned_by_id)

        if isinstance(self.created_by_id, str) and self.created_by_id.isdigit():
            self.created_by_id = int(self.created_by_id)

        if isinstance(self.modified_by_id, str) and self.modified_by_id.isdigit():
            self.modified_by_id = int(self.modified_by_id)

    def get_primary_email(self) -> str | None:
        """Получение основного email-адреса контакта.

        :return: Основной email или None, если email не указан
        """
        if not self.email:
            return None

        for email in self.email:
            if email.value_type == 'WORK':
                return email.value

        return self.email[0].value

    def get_primary_phone(self) -> str | None:
        """Получение основного номера телефона контакта.

        :return: Основной телефон или None, если телефон не указан
        """
        if not self.phone:
            return None

        for phone in self.phone:
            if phone.value_type == 'WORK':
                return phone.value

        for phone in self.phone:
            if phone.value_type == 'MOBILE':
                return phone.value

        return self.phone[0].value

    def get_full_name(self) -> str:
        """Получение полного имени контакта.

        :return: Полное имя контакта
        """
        parts = []

        if self.last_name:
            parts.append(self.last_name)

        if self.name:
            parts.append(self.name)

        if self.second_name:
            parts.append(self.second_name)

        return ' '.join(parts) if parts else 'Неизвестный контакт'
