# -*- coding: utf-8 -*-
# Copyright 2017 Denis Leemann, Camptocamp SA
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

from odoo import models, fields, api


class ManualDeliveryLine(models.TransientModel):
    _name = "manual.delivery.line"

    manual_delivery_id = fields.Many2one(
        'manual.delivery',
        string='Wizard manual procurement',
    )
    order_line_id = fields.Many2one(
        'sale.order.line',
        string='Sale Order Line',
        readonly=True,
    )
    product_id = fields.Many2one(
        'product.product',
        string='Product',
        related='order_line_id.product_id',
        readonly=True
    )
    ordered_qty = fields.Float(
        'Ordered quantity',
        help = "Quantity ordered in the related Sale Order",
        readonly=True,
    )
    existing_qty = fields.Float(
        'Existing quantity',
        help = "Quantity already planned or shipped (stock movements \
            already created)",
        readonly=True,
    )
    remaining_qty = fields.Float(
        'Remaining quantity',
        compute='compute_remaining_qty',
        help = "Remaining quantity available to deliver",
        readonly=True,
    )
    to_ship_qty = fields.Float(
        'Quantity to Ship',
    )

    @api.multi
    @api.depends('to_ship_qty')
    def compute_remaining_qty(self):
        for line in self:
            line.remaining_qty = line.ordered_qty - line.existing_qty \
                - line.to_ship_qty
