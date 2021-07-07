# Copyright 2020 Tecnativa - Carlos Roca
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl.html).
from odoo import api, fields, models


# We overwrite this class as a trick to repeat the product_id field with different
# attributes on the view.
class SaleOrderLine(models.Model):
    _inherit = "sale.order.line"

    product_allowed_id = fields.Many2one(
        related="product_id", string="Product with allowed list"
    )

    @api.onchange("product_allowed_id")
    def _onchange_product_secondary_fields(self):
        if self.product_allowed_id:
            self.product_id = self.product_allowed_id
