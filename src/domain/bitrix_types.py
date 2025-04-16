"""Модуль с определением типов данных Bitrix24.

Содержит классы, представляющие различные типы данных из Bitrix24 API.
"""

from dataclasses import dataclass
from datetime import UTC, datetime
from typing import Any, Self

type BitrixID = int
type BitrixCurrencyID = str
type BitrixStageID = str
type BitrixCategoryID = int


@dataclass
class BitrixMultiField:
    """Представление мультиполей Bitrix24 (EMAIL, PHONE, WEB и т.д.).

    Пример:
    {
        "ID": "123",
        "VALUE_TYPE": "WORK",
        "VALUE": "test@example.com",
        "TYPE_ID": "EMAIL"
    }
    """

    value: str
    value_type: str
    type_id: str
    id: int | None = None

    @classmethod
    def from_bitrix(cls, data: dict[str, Any]) -> 'BitrixMultiField':
        """Создание объекта из данных Bitrix24.

        :param data: Словарь с данными из API Bitrix24
        :return: Объект мультиполя
        """
        return cls(
            value=data.get('VALUE', ''),
            value_type=data.get('VALUE_TYPE', ''),
            type_id=data.get('TYPE_ID', ''),
            id=int(data.get('ID')) if data.get('ID') else None,  # type: ignore[arg-type]
        )

    def to_bitrix(self) -> dict[str, Any]:
        """Преобразование в формат для API Bitrix24.

        :return: Словарь для отправки в API
        """
        result = {
            'VALUE': self.value,
            'VALUE_TYPE': self.value_type,
            'TYPE_ID': self.type_id,
        }
        if self.id is not None:
            result['ID'] = str(self.id)
        return result

    def __getitem__(self, key: str) -> str | int | None:
        """Поддержка словарного доступа к полям объекта.

        :param key: Ключ поля
        :return: Значение поля
        :raises KeyError: Если ключ не найден
        """
        return getattr(self, key.lower())


class BitrixDate(str):
    """Дата в формате Bitrix24 (YYYY-MM-DD)."""

    __slots__ = ()  # Определение пустого кортежа слотов

    @classmethod
    def from_datetime(cls, dt: datetime) -> Self:
        """Создать BitrixDate из объекта datetime.

        :param dt: Объект datetime
        :return: BitrixDate в формате YYYY-MM-DD
        """
        return cls(dt.strftime('%Y-%m-%d'))

    def to_datetime(self) -> datetime:
        """Преобразовать в объект datetime.

        :return: Объект datetime
        """
        return datetime.strptime(str(self), '%Y-%m-%d').replace(
            tzinfo=UTC,
        )


class BitrixDateTime(str):
    """Дата и время в формате Bitrix24 (YYYY-MM-DD HH:MM:SS)."""

    __slots__ = ()

    @classmethod
    def from_datetime(cls, dt: datetime) -> Self:
        """Создать BitrixDateTime из объекта datetime.

        :param dt: Объект datetime
        :return: BitrixDateTime в формате YYYY-MM-DD HH:MM:SS
        """
        return cls(dt.strftime('%Y-%m-%d %H:%M:%S'))

    def to_datetime(self) -> datetime:
        """Преобразовать в объект datetime.

        :return: Объект datetime
        """
        return datetime.strptime(
            str(self),
            '%Y-%m-%d %H:%M:%S %z',
        ).replace(tzinfo=UTC)
