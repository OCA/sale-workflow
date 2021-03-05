# Copyright 2017 Eficent Business and IT Consulting Services S.L.
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl.html).

from odoo import api, fields, models


class SaleOrder(models.Model):
    _inherit = "sale.order"

    force_invoiced = fields.Boolean(
        string="Force invoiced",
        help="When you set this field, the sales order will be considered as "
        "fully invoiced, even when there may be ordered or delivered "
        "quantities pending to invoice.",
        readonly=True,
        states={"done": [("readonly", False)]},
        copy=False,
    )

    @api.depends("force_invoiced")
    def _get_invoiced(self):
        super(SaleOrder, self)._get_invoiced()
        for order in self.filtered(
            lambda so: so.force_invoiced and so.invoice_status == "to invoice"
        ):
            order.invoice_status = "invoiced"
        deposit_product_id = self.env["sale.advance.payment.inv"]._default_product_id()
        line_invoice_status_all = [
            (d["order_id"][0], d["invoice_status"])
            for d in self.env["sale.order.line"].read_group(
                [
                    ("order_id", "in", self.ids),
                    ("product_id", "!=", deposit_product_id.id),
                ],
                ["order_id", "invoice_status"],
                ["order_id", "invoice_status"],
                lazy=False,
            )
        ]
        for order in self.filtered(
            lambda so: not so.force_invoiced and so.invoice_status == "invoiced"
        ):
            line_invoice_status = [
                d[1] for d in line_invoice_status_all if d[0] == order.id
            ]
            if any(
                invoice_status == "to invoice" for invoice_status in line_invoice_status
            ):
                order.invoice_status = "to invoice"
