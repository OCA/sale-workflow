# -*- coding: utf-8 -*-
# Copyright 2017 Denis Leemann, Camptocamp SA
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

from odoo import models, fields, api
import odoo.addons.decimal_precision as dp


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
    line_description = fields.Text(
        string='Description',
        related='order_line_id.name',
        readonly=True
    )
    ordered_qty = fields.Float(
        'Ordered quantity',
        help="Quantity ordered in the related Sale Order",
        readonly=True,
        digits=dp.get_precision('Product Unit of Measure')
    )
    existing_qty = fields.Float(
        'Existing quantity',
        help="Quantity already planned or shipped (stock movements \
            already created)",
        readonly=True,
        digits=dp.get_precision('Product Unit of Measure')
    )
    remaining_qty = fields.Float(
        'Remaining quantity',
        compute='_compute_remaining_qty',
        help="Remaining quantity available to deliver",
        readonly=True,
        digits=dp.get_precision('Product Unit of Measure')
    )
    to_ship_qty = fields.Float(
        'Quantity to Ship',
        digits=dp.get_precision('Product Unit of Measure')
    )

    @api.multi
    @api.depends('to_ship_qty')
    def _compute_remaining_qty(self):
        for line in self:
            line.remaining_qty = line.ordered_qty - line.existing_qty \
                - line.to_ship_qty
