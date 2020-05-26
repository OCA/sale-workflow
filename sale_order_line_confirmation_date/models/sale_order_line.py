# -*- coding: utf-8 -*-
# Copyright 2020 ACSONE SA/NV
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo import fields, models


class SaleOrderLine(models.Model):

    _inherit = 'sale.order.line'

    confirmation_date = fields.Datetime(
        related="order_id.confirmation_date",
        store=True,
    )
