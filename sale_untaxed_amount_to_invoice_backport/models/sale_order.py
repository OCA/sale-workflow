from odoo import fields, models


class SaleOrder(models.Model):
    _inherit = 'sale.order'

    untaxed_amount_to_invoice = fields.Monetary(
        string='Untaxed amount to invoice',
        compute='_compute_untaxed_amount')
    untaxed_amount_invoiced = fields.Monetary(
        string='Untaxed amount invoice',
        compute='_compute_untaxed_amount')

    def _compute_untaxed_amount(self):
        """Compute the total untaxed amount to invoice of the SO."""
        for order in self:
            order.untaxed_amount_to_invoice = sum(order.order_line.mapped(
                "untaxed_amount_to_invoice"
            ))
            order.untaxed_amount_invoiced = sum(order.order_line.mapped(
                "untaxed_amount_invoiced"
            ))
