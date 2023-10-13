# Copyright 2018 Tecnativa - Sergio Teruel
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).

from odoo import api, fields, models
from odoo.osv import expression


class SaleOrderLine(models.Model):
    _inherit = "sale.order.line"

    discount = fields.Float(
        compute="_compute_discount",
        store=True,
        readonly=False,
    )

    @api.model
    def get_discount_vals_for_product(self, product_id, order_id):
        domain = order_id.company_id.sudo()._get_general_discount_eval_domain()
        if domain:
            domain = expression.AND([[("id", "=", product_id.id)], domain])
            if not self.env["product.product"].sudo().search(domain):
                return {}
        return {"discount": order_id.general_discount}

    @api.depends("order_id", "order_id.general_discount", "product_id")
    def _compute_discount(self):
        if hasattr(super(), "_compute_discount"):
            super()._compute_discount()
        for line in self:
            discount_vals = line.get_discount_vals_for_product(
                line.product_id, line.order_id
            )
            # support future extensions such as sale_order_general_discount_triple
            for field, value in discount_vals.items():
                line[field] = value
