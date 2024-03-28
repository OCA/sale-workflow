# Copyright 2017 ForgeFlow S.L.
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl.html).

from odoo import api, fields, models


class SaleOrder(models.Model):
    _inherit = "sale.order"

    force_invoiced = fields.Boolean(
        help="When you set this field, the sales order will be considered as "
        "fully invoiced, even when there may be ordered or delivered "
        "quantities pending to invoice.",
        readonly=True,
        tracking=20,
        copy=False,
    )

    @api.depends("force_invoiced")
    def _compute_invoice_status(self):
        res = super()._compute_invoice_status()
        self.filtered(lambda so: so.force_invoiced and so.state == "sale").update(
            {"invoice_status": "invoiced"}
        )
        return res
