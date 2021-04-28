# Copyright 2017 ForgeFlow S.L.
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
        states={"done": [("readonly", False)], "sale": [("readonly", False)]},
        copy=False,
    )

    @api.depends("force_invoiced")
    def _get_invoice_status(self):
        super(SaleOrder, self)._get_invoice_status()
        for order in self.filtered(
            lambda so: so.force_invoiced and so.state in ("sale", "done")
        ):
            order.invoice_status = "invoiced"
