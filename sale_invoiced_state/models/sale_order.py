# Copyright 2022 PyTech SRL - Alessandro Uffreduzzi
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo import api, fields, models
from odoo.tools import float_is_zero, float_compare


class SaleOrder(models.Model):
    _inherit = "sale.order"

    invoiced_state = fields.Selection(
        [
            ("not_invoiced", "Not Invoiced"),
            ("downpayment", "Only Downpayment"),
            ("partially", "Partially Invoiced"),
            ("invoiced", "Fully Invoiced"),
        ],
        compute="_compute_invoiced_state",
        store=True,
        string="Invoiced",
    )

    @api.multi
    def all_invoiced(self):
        self.ensure_one()
        precision = self.env["decimal.precision"].precision_get(
            "Product Unit of Measure"
        )

        return all(
            float_compare(
                line.product_uom_qty,
                line.qty_invoiced,
                precision_digits=precision,
            )
            == 0
            for line in self.order_line
        )

    def only_downpayment_invoiced(self):
        self.ensure_one()
        precision = self.env["decimal.precision"].precision_get(
            "Product Unit of Measure"
        )

        downpayment_lines = self.order_line.filtered("is_downpayment")
        # If there are no downpayment lines
        # or they have not been invoiced
        if not downpayment_lines or all(
            float_is_zero(line.qty_invoiced, precision_digits=precision)
            for line in downpayment_lines
        ):
            return False

        order_lines = self.order_line - downpayment_lines

        if all(
            float_is_zero(line.qty_invoiced, precision_digits=precision)
            for line in order_lines
        ):
            return True
        return False

    def any_lines_invoiced(self):
        self.ensure_one()
        precision = self.env["decimal.precision"].precision_get(
            "Product Unit of Measure"
        )
        return any(
            not float_is_zero(line.qty_invoiced, precision_digits=precision)
            for line in self.order_line
        )

    @api.depends(
        "state",
        "order_line.product_uom_qty",
        "order_line.qty_invoiced",
    )
    def _compute_invoiced_state(self):
        for order in self:
            if order.state not in ("sale", "done"):
                order.invoiced_state = "not_invoiced"
            elif order.all_invoiced():
                order.invoiced_state = "invoiced"
            elif order.only_downpayment_invoiced():
                order.invoiced_state = "downpayment"
            elif order.any_lines_invoiced():
                order.invoiced_state = "partially"
            else:
                order.invoiced_state = "not_invoiced"
