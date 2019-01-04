# -*- coding: utf-8 -*-
# Copyright 2018 Akretion (http://www.akretion.com).
# @author Pierrick BRUN <pierrick.brun@akretion.com>
# Copyright 2018 Camptocamp
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo import models, fields, api
from odoo.tools import float_is_zero, float_compare


class SaleOrder(models.Model):
    _inherit = 'sale.order'

    delivery_state = fields.Selection([
        ('no', 'No delivery'),
        ('unprocessed', 'Unprocessed'),
        ('partially', 'Partially processed'),
        ('done', 'Done')],
        string='Delivery state',
        compute='_compute_delivery_state',
        store=True
    )

    def _all_qty_delivered(self):
        """
        Returns True if all line have qty_delivered >= to ordered quantities

        If `delivery` module is installed, ignores the lines with delivery costs

        :returns: boolean
        """
        self.ensure_one()
        # Skip delivery costs lines
        sale_lines = self.order_line
        Carrier = self.env.get('delivery.carrier')
        if Carrier:
            sale_lines = sale_lines.filtered(
                lambda rec: not rec.is_delivery_cost())
        precision = self.env['decimal.precision'].precision_get(
            'Product Unit of Measure'
        )
        return all(
            float_compare(line.qty_delivered, line.product_uom_qty,
                          precision_digits=precision) >= 0
            for line in sale_lines
        )

    def _partially_delivered(self):
        """
        Returns True if at least one line is delivered

        :returns: boolean
        """
        self.ensure_one()
        # Skip delivery costs lines
        sale_lines = self.order_line
        Carrier = self.env.get('delivery.carrier')
        if Carrier:
            sale_lines = sale_lines.filtered(
                lambda rec: not rec.is_delivery_cost())
        precision = self.env['decimal.precision'].precision_get(
            'Product Unit of Measure'
        )
        return any(
            not float_is_zero(line.qty_delivered, precision_digits=precision)
            for line in self.order_line
        )

    @api.depends('order_line', 'order_line.qty_delivered', 'state')
    def _compute_delivery_state(self):
        for order in self:
            if order.state in ('draft', 'cancel'):
                order.delivery_state = 'no'
            elif order._all_qty_delivered():
                order.delivery_state = 'done'
            elif order._partially_delivered():
                order.delivery_state = 'partially'
            else:
                order.delivery_state = 'unprocessed'


class SaleOrderLine(models.Model):
    _inherit = 'sale.order.line'

    def is_delivery_cost(self):
        """
        Returns if a sale line has a delivery products
        check that a line is a delivery costs

        :returns boolean:
        """
        self.ensure_one()
        Carrier = self.env.get('delivery.carrier')
        # If you call this without `delivery` module installed
        # you are probably doing it wrong because it will always
        # returns False
        if not Carrier or not self.product_id:
            return False
        search_domain = [('product_id', '=', self.product_id.id)]
        return bool(Carrier.search_count(search_domain))
