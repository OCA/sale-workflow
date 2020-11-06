# -*- coding: utf-8 -*-
# Copyright 2017 Denis Leemann, Camptocamp SA
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).
from odoo import fields, models, api


class SaleOrderLine(models.Model):
    _inherit = 'sale.order.line'

    existing_qty = fields.Float(
        'Existing quantity',
        compute='_get_existing_qty',
        help = "Quantity already planned or shipped (stock movements \
            already created)",
        readonly=True,
    )

    @api.multi
    def _action_procurement_create(self):
        for line in self:
            if (line.order_id.manual_delivery and
                    line.product_id.type != 'service'):
                return self.env['procurement.order'].browse()
            else:
                return super(SaleOrderLine, self)._action_procurement_create()

    @api.multi
    def _compute_get_existing_qty(self):
        """Computes the remai quantity on sale order lines, based on done
        stock moves related to its procurements
        """
        for line in self:
            qty = 0.0
            for move in line.procurement_ids.mapped('move_ids').filtered(
                    lambda r: r.state not in ('draft', 'cancel')
                    and not r.scrapped):
                if move.location_dest_id.usage == "customer":
                    qty += move.product_uom._compute_quantity(
                        move.product_uom_qty, 
                        line.product_uom)
                elif move.location_dest_id.usage == "internal" \
                    and move.to_refund_so:
                    qty -= move.product_uom._compute_quantity(
                        move.product_uom_qty,
                        line.product_uom)
            line.existing_qty = qty
