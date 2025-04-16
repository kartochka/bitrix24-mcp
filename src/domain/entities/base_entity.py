"""Модуль с базовыми классами сущностей Bitrix24.

Содержит абстрактный базовый класс для всех сущностей Bitrix24.
"""

import json
from dataclasses import asdict, dataclass, field
from typing import Any, ClassVar, Self


@dataclass
class BitrixEntity:
    """Базовый класс для всех сущностей Bitrix24.

    Содержит общие атрибуты и методы для всех сущностей Bitrix24.
    """

    id: int
    additional_fields: dict[str, Any] = field(default_factory=dict)

    _bitrix_field_mapping: ClassVar[dict[str, str]] = {
        'ID': 'id',
    }

    @classmethod
    def from_bitrix(cls, data: dict[str, Any]) -> Self:
        """Создание объекта из данных Bitrix24.

        :param data: Словарь с данными из API Bitrix24
        :return: Объект сущности
        """
        if order_data := data.get('order0000000000'):
            data = order_data
        entity_data = {}
        additional_fields: dict[str, Any] = {}

        for bitrix_field, entity_field in cls._bitrix_field_mapping.items():
            if bitrix_field in data:
                entity_data[entity_field] = data[bitrix_field]

        additional_fields = {
            **additional_fields,
            **{k: v for k, v in data.items() if k not in cls._bitrix_field_mapping},
        }

        entity_data['additional_fields'] = additional_fields

        return cls(**entity_data)

    def to_bitrix(self) -> dict[str, Any]:
        """Преобразование в формат для API Bitrix24.

        :return: Словарь для отправки в API
        """
        data = {}

        reverse_mapping = {v: k for k, v in self._bitrix_field_mapping.items()}

        for entity_field, bitrix_field in reverse_mapping.items():
            if hasattr(self, entity_field):
                data[bitrix_field] = getattr(self, entity_field)

        return {**data, **dict(self.additional_fields.items())}

    def to_str_json(self) -> str:
        """Преобразует объект в json строку.

        :return: Словарь с атрибутами объекта
        """
        return json.dumps(asdict(self))
