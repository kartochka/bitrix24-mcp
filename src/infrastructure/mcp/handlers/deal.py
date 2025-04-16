"""Модуль с обработчиками MCP для сделок.

Содержит обработчики инструментов и ресурсов для работы со сделками Bitrix24.
"""

import json
from typing import Any

from src.application.services.deal import DealService
from src.domain.entities.deal import Deal
from src.infrastructure.ioc import container
from src.infrastructure.logging.logger import logger
from src.infrastructure.mcp.server import BitrixMCPServer


def register_deal_handlers(mcp_server: BitrixMCPServer) -> None:
    """Регистрация обработчиков для работы со сделками.

    :param mcp_server: Экземпляр MCP сервера
    """
    mcp_server.add_tool(
        get_deal,
        name='get_deal',
        description='Получение информации о сделке по ID',
    )

    mcp_server.add_tool(
        list_deals,
        name='list_deals',
        description='Получение списка сделок с возможностью фильтрации',
    )

    mcp_server.add_tool(
        update_deal_stage,
        name='update_deal_stage',
        description='Обновление стадии сделки',
    )

    mcp_server.add_resource(
        'deal://{deal_id}',
        get_deal_resource,
        description='Получение данных сделки по ID',
    )

    mcp_server.add_resource(
        'deals://active',
        get_active_deals_resource,
        description='Получение списка активных сделок',
    )

    logger.info('Зарегистрированы обработчики для работы со сделками')


async def get_deal(
    deal_id: int,
) -> str:
    """Получение сделки по ID (инструмент).

    :param deal_id: Идентификатор сделки
    :return: JSON-строка с данными сделки или сообщение об ошибке
    """
    deal_service = container.get(DealService)
    deal = await deal_service.get_deal_by_id(deal_id)
    if not deal:
        return json.dumps({'error': f'Сделка с ID={deal_id} не найдена'})
    return deal.to_str_json()


async def list_deals(
    active_only: bool = False,
    contact_id: int | None = None,
    company_id: int | None = None,
    limit: int | None = None,
) -> str:
    """Получение списка сделок (инструмент).

    :param active_only: Только активные сделки
    :param contact_id: Идентификатор контакта для фильтрации (опционально)
    :param company_id: Идентификатор компании для фильтрации (опционально)
    :param limit: Максимальное количество результатов
    :return: JSON-строка со списком сделок
    """
    if not limit:
        limit = 50
    deal_service = container.get(DealService)
    deals = await deal_service.list_deals(
        active_only,
        contact_id,
        company_id,
        limit,
    )

    filter_info: dict[str, Any] = {'active_only': active_only}

    if contact_id:
        filter_info['contact_id'] = contact_id

    if company_id:
        filter_info['company_id'] = company_id

    result = {
        'total': len(deals),
        'filters': filter_info,
        'deals': [json.loads(deal.to_str_json()) for deal in deals],
    }

    return json.dumps(result)


async def update_deal_stage(
    deal_id: int,
    stage_id: str,
) -> str:
    """Обновление стадии сделки (инструмент).

    :param deal_id: Идентификатор сделки
    :param stage_id: Идентификатор новой стадии
    :return: JSON-строка с результатом операции
    """
    deal_service = container.get(DealService)
    success = await deal_service.update_deal_stage(deal_id, stage_id)

    result = {
        'success': success,
        'message': (
            f'Стадия сделки ID={deal_id} '
            f'{"успешно обновлена" if success else "не обновлена"} на {stage_id}'
        ),
    }

    return json.dumps(result)


async def get_deal_resource(
    deal_id: str,
) -> str:
    """Получение данных сделки в виде ресурса.

    :param deal_id: Идентификатор сделки
    :param deal_service: Сервис для работы со сделками (внедряется через DI)
    :return: Строковое представление данных сделки
    """
    deal_service = container.get(DealService)
    try:
        deal_id_int = int(deal_id)
        deal = await deal_service.get_deal_by_id(deal_id_int)

        if not deal:
            return f'Сделка с ID={deal_id} не найдена'

        return _format_deal_for_display(deal)
    except ValueError:
        return f'Некорректный ID сделки: {deal_id}'


async def get_active_deals_resource() -> str:
    """Получение списка активных сделок в виде ресурса.

    :param limit: Максимальное количество сделок
    :return: Строковое представление списка сделок
    """
    deal_service = container.get(DealService)
    deals = await deal_service.list_deals(active_only=True)

    if not deals:
        return 'Активные сделки не найдены'

    lines = [f'Активные сделки ({len(deals)}):']

    for i, deal in enumerate(deals, 1):
        lines.append(f'{i}. {deal.title} (ID: {deal.id})')
        lines.append(f'   Стадия: {deal.stage_id}')
        lines.append(f'   Сумма: {deal.opportunity} {deal.currency_id}')
        lines.append('')

    return '\n'.join(lines)


def _format_deal_for_display(deal: Deal) -> str:
    """Форматирование сделки для читаемого отображения.

    :param deal: Объект сделки
    :return: Форматированная строка с данными сделки
    """
    lines = [
        f'Сделка ID: {deal.id}',
        f'Название: {deal.title}',
        f'Стадия: {deal.stage_id}',
        f'Сумма: {deal.opportunity} {deal.currency_id}',
        f'Компания ID: {deal.company_id or "Не указана"}',
        f'Ответственный: {deal.assigned_by_id or "Не назначен"}',
        f'Дата создания: {deal.date_create or "Неизвестно"}',
        f'Статус: {"Активная" if deal.is_active() else "Завершенная"}',
    ]

    if deal.contact_ids:
        lines.append(
            f'Связанные контакты: {", ".join(map(str, deal.contact_ids))}',
        )
    else:
        lines.append('Связанные контакты: Отсутствуют')

    return '\n'.join(lines)
