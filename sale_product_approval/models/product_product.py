# Copyright 2021 Open Source Integrators
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).

from odoo import api, fields, models


class ProductTemplate(models.Model):
    _inherit = "product.template"

    sale_ok = fields.Boolean(
        compute="_compute_sale_ok_product",
        string="Can be Sold",
        default=False,
        store=True,
    )
    candidate_sale = fields.Boolean(
        string="Candidate to be Sold",
        default=True,
    )

    @api.depends("candidate_sale", "product_state_id.approved_sale")
    def _compute_sale_ok_product(self):
        for product in self:
            if product.product_state_id:
                product.sale_ok = (
                    product.candidate_sale and product.product_state_id.approved_sale
                )
                if not product.sale_ok:
                    order_ids = (
                        self.env["sale.order.line"]
                        .search(
                            [
                                ("product_id", "in", product.product_variant_ids.ids),
                                ("state", "in", ["draft", "sent"]),
                                ("approved_sale", "=", True),
                            ]
                        )
                        .mapped("order_id")
                    )
                    order_ids._log_exception_activity_sale(product)

    @api.model
    def _get_default_product_state_id(self):
        return self.env.ref(
            "product_state.product_state_draft", raise_if_not_found=False
        )
