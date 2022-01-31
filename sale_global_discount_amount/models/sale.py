# Copyright 2020 Akretion France (http://www.akretion.com)
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo import api, models


class SaleOrder(models.Model):
    _inherit = ["sale.order", "discount.mixin"]
    _name = "sale.order"
    _gd_lines_field = "order_line"
    _gd_tax_field = "tax_id"

    def _get_discount_amount_to_invoice(self, move_type):
        # This is a really simple implementation of partial discount invoicing
        # we alway invoice all discount, then the user can change it
        # when invoicing a backorder we invoice the discount that have been not yet
        # invoiced instead of invoicing all again
        # depending of your company need/process you can inherit this method
        invoiced_amount = sum(
            [
                inv.global_discount_amount
                for inv in self.invoice_ids
                if inv.move_type == move_type
            ]
        )
        return self.global_discount_amount - invoiced_amount

    def _prepare_invoice(self):
        self.ensure_one()
        invoice_vals = super()._prepare_invoice()
        invoice_vals["global_discount_amount"] = self._get_discount_amount_to_invoice(
            invoice_vals["move_type"]
        )
        return invoice_vals


class SaleOrderLine(models.Model):
    _inherit = ["sale.order.line", "discount.line.mixin"]
    _name = "sale.order.line"

    def _prepare_invoice_line(self, **optional_values):
        self.ensure_one()
        invoice_line_vals = super()._prepare_invoice_line(**optional_values)
        invoice_line_vals["is_discount_line"] = self.is_discount_line
        return invoice_line_vals

    @api.depends("is_discount_line")
    def _get_to_invoice_qty(self):
        discount_lines = self.filtered("is_discount_line")
        for line in discount_lines:
            line.qty_to_invoice = 0
        super(SaleOrderLine, self - discount_lines)._get_to_invoice_qty()

    @api.depends("is_discount_line")
    def _get_invoice_qty(self):
        discount_lines = self.filtered("is_discount_line")
        for line in discount_lines:
            line.qty_invoiced = 0
        super(SaleOrderLine, self - discount_lines)._get_invoice_qty()

    @api.depends("is_discount_line")
    def _compute_invoice_status(self):
        discount_lines = self.filtered("is_discount_line")
        for line in discount_lines:
            # We always consider this line as invoiced to not impact the
            # invoice status of the sale order
            line.invoice_status = "invoiced"
        super(SaleOrderLine, self - discount_lines)._compute_invoice_status()
