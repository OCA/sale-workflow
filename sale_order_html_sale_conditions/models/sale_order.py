# Copyright 2021 Camptocamp SA
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo import api, fields, models


class SaleOrder(models.Model):
    _inherit = "sale.order"

    @api.model
    def _default_sale_conditions(self):
        return self.env.company.default_sale_conditions or ""

    sale_conditions = fields.Html(
        readonly=True,
        states={"draft": [("readonly", False)]},
        default=_default_sale_conditions,
    )
