# -*- coding: utf-8 -*-
# Copyright 2018 ACSONE SA/NV
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo import api, fields, models
from odoo.tools import float_compare


class SaleOrderLine(models.Model):

    _inherit = 'sale.order.line'

    to_be_procured = fields.Boolean(
        compute='_compute_to_be_procured',
    )
    pickings_in_progress = fields.Boolean(
        compute='_compute_pickings_in_progress'
    )

    @api.multi
    @api.depends('order_id.picking_ids.can_be_amended')
    def _compute_pickings_in_progress(self):
        """
        Compute the picking in progress. That depends on picking
        'can_be_amended' state. If one is not in the 'can_be_amended' state,
        we are in the 'pickings_in_progress' situation.
        :return:
        """
        for line in self.filtered(
                lambda l: any(
                    picking.state != 'cancel' and
                    not picking.can_be_amended
                    for picking in l.order_id.picking_ids)):
            line.pickings_in_progress = True

    @api.multi
    @api.depends(
        'procurement_ids',
        'procurement_ids.state',
        'procurement_ids.product_qty',
        'product_uom_qty')
    def _compute_to_be_procured(self):
        """
        This compare the current procurement quantities (see Odoo
        _action_procurement_create function)
        :return:
        """
        precision = self.env['decimal.precision'].precision_get(
            'Product Unit of Measure')
        for line in self:
            qty = 0.0
            for proc in line.procurement_ids.filtered(
                    lambda p: p.state != 'cancel'):
                qty += proc.product_qty
            if float_compare(
                    qty,
                    line.product_uom_qty,
                    precision_digits=precision) < 0:
                line.to_be_procured = True

    @api.multi
    def write(self, values):
        precision = self.env['decimal.precision'].precision_get(
            'Product Unit of Measure')
        lines_lower = self.env['sale.order.line'].browse()
        if 'product_uom_qty' in values:
            lines_lower = self.filtered(
                lambda l: l.state == 'sale' and
                float_compare(
                    l.product_uom_qty,
                    values['product_uom_qty'],
                    precision_digits=precision) > 0)
        res = super(SaleOrderLine, self).write(values)
        if 'product_uom_qty' in values:
            # Quantities has changed
            # Check if procurement has to be created
            for line in lines_lower:
                if not line.pickings_in_progress:
                    # LIMITATION - Don't take all procurement at once here
                    for procurement in line.procurement_ids:
                        procurement.cancel()
            self.filtered(
                lambda line: line.state == 'sale' and
                line.to_be_procured)._action_procurement_create()
        return res
