"""Пакет с миксинами для работы с API Bitrix24.

Миксины предоставляют функциональность для различных аспектов
взаимодействия с API Bitrix24.
"""

from src.infrastructure.bitrix.mixins.batch_operations import (
    BitrixBatchOperationsMixin,
)
from src.infrastructure.bitrix.mixins.filter_builder import (
    BitrixFilterBuilderMixin,
)
from src.infrastructure.bitrix.mixins.pagination import BitrixPaginationMixin
from src.infrastructure.bitrix.mixins.read import BitrixReadMixin
from src.infrastructure.bitrix.mixins.relationship import (
    BitrixRelationshipMixin,
)
from src.infrastructure.bitrix.mixins.write import BitrixWriteMixin

__all__ = [
    'BitrixBatchOperationsMixin',
    'BitrixFilterBuilderMixin',
    'BitrixPaginationMixin',
    'BitrixReadMixin',
    'BitrixRelationshipMixin',
    'BitrixWriteMixin',
]
