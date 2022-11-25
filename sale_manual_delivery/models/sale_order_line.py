# -*- coding: utf-8 -*-
# Copyright 2017 Denis Leemann, Camptocamp SA
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).
from odoo import fields, models, api
from odoo.tools import float_compare


class SaleOrderLine(models.Model):
    _inherit = 'sale.order.line'

    existing_qty = fields.Float(
        'Existing quantity',
        compute='_compute_existing_qty',
        help="Quantity already planned or shipped (stock movements \
            already created)"
    )

    pending_qty_to_deliver = fields.Boolean(
        compute='_compute_existing_qty',
        store=True,
        readonly=True,
        string='There is Pending qty to add to a delivery')

    @api.multi
    def _action_procurement_create(self):
        normal_lines = self.filtered(lambda l: not l.order_id.manual_delivery)
        new_procs = super(
            SaleOrderLine, normal_lines)._action_procurement_create()
        return new_procs

    @api.depends('procurement_ids', 'procurement_ids.state', 'order_id.state',
                 'procurement_ids.move_ids.state', 'procurement_ids.move_ids')
    @api.multi
    def _compute_existing_qty(self):
        """Computes the remaining quantity on sale order lines, based on done
        stock moves related to its procurements
        """
        for line in self:
            rounding = line.company_id.currency_id.rounding
            qty = 0.0
            for move in line.procurement_ids.mapped('move_ids').filtered(
                    lambda r: r.state not in ('draft', 'cancel') and
                    not r.scrapped):
                if move.location_dest_id.usage == "customer":
                    qty += move.product_uom._compute_quantity(
                        move.product_uom_qty,
                        line.product_uom)
                elif (move.location_dest_id.usage == "internal" and
                        move.to_refund_so):
                    qty -= move.product_uom._compute_quantity(
                        move.product_uom_qty,
                        line.product_uom)
            line.existing_qty = qty
            if float_compare(
                    line.product_uom_qty,
                    line.existing_qty, precision_rounding=rounding):
                line.pending_qty_to_deliver = True
            else:
                line.pending_qty_to_deliver = False
