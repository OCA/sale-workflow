# -*- coding: utf-8 -*-
# Copyright 2020 ACSONE SA/NV (<http://acsone.eu>)
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).
import logging
from odoo import api, SUPERUSER_ID

_logger = logging.getLogger(__name__)
try:
    from openupgradelib.openupgrade import add_fields
except (ImportError, IOError) as err:
    _logger.debug(err)


def pre_init_hook(cr):
    env = api.Environment(cr, SUPERUSER_ID, {})
    fields_list = [(
        'confirmation_date',
        'sale.order.line',
        False,
        'datetime',
        'timestamp',
        'sale_order_line_confirmation_date',
    )]
    add_fields(env, fields_list)
    cr.execute("""
        UPDATE sale_order_line
        SET confirmation_date = so.confirmation_date
        FROM sale_order AS so
        WHERE so.id = sale_order_line.order_id
        AND so.confirmation_date IS NOT NULL
    """)
