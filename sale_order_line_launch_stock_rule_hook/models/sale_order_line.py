# Copyright 2023 ForgeFlow S.L.
# License LGPL-3.0 or later (https://www.gnu.org/licenses/lgpl).

from odoo import api, models


class SaleOrderLine(models.Model):
    _inherit = "sale.order.line"

    @api.model
    def _skip_procurement(self):
        self.ensure_one()
        # Ignore flake8 error to respect original Odoo condition.
        # flake8: noqa: E713
        return self.state != "sale" or not self.product_id.type in ("consu", "product")
