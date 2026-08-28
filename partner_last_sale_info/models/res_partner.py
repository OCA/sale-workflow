# Copyright 2026 Open Source Integrators
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo import api, fields, models


class ResPartner(models.Model):
    _inherit = "res.partner"

    last_sale_order_date = fields.Datetime(
        compute="_compute_last_sale_order_date",
        store=True,
        readonly=False,  # Allows data imports
        help="Date of the last sale order for this customer",
    )
    last_sale_order_id = fields.Many2one(
        "sale.order",
        compute="_compute_last_sale_order_date",
        store=True,
        readonly=False,
        help="Last sale order for this customer",
    )

    @api.depends("sale_order_ids")
    def _compute_last_sale_order_date(self):
        for partner in self:
            last_order = self.env["sale.order"].search(
                [("partner_id", "=", partner.id), ("state", "=", "sale")],
                order="date_order desc",
                limit=1,
            )
            if last_order:
                partner.last_sale_order_date = last_order.date_order
                partner.last_sale_order_id = last_order
            # Do not reset any imported data when a quotation is created
