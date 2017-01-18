# -*- coding: utf-8 -*-
# Copyright 2017 Denis Leemann, Camptocamp SA
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

from odoo import models, fields


class ManualProcurement(models.TransientModel):
    _name = "manual.line"

    manual_proc_id = fields.Many2one(
        'manual.procurement',
        string='Wizard manual procurement',
    )
    order_line_id = fields.Many2one(
        'sale.order.line',
        string='Sale Order Line',
        readonly=True,
    )
    ordered_qty = fields.Float(
        'Ordered Quantity',
    )
    remaining = fields.Float(
        'Computed remaining to ship',
    )
    product_qty = fields.Float(
        'Quantity to Ship',
    )
