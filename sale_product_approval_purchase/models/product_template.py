# Copyright 2021 Open Source Integrators
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).

from odoo import api, fields, models


class ProductTemplate(models.Model):
    _inherit = "product.template"

    purchase_ok = fields.Boolean(
        string="Can be Purchased",
        copy=False,
        readonly=True,
    )
    candidate_purchase = fields.Boolean(string="Candidate to be Purchased")

    @api.model
    def create(self, vals):
        new = super().create(vals)
        new._set_purchase_ok()
        return new

    def write(self, vals):
        res = super().write(vals)
        if "product_state_id" in vals:
            to_state = self.product_state_id.code
            to_state != "draft" and self._set_purchase_ok()
        return res

    def _set_purchase_ok(self):
        for product in self:
            if product.product_state_id:
                product.purchase_ok = (
                    product.candidate_purchase
                    and product.product_state_id.approved_purchase
                )
                if not product.purchase_ok:
                    order_ids = (
                        self.env["purchase.order.line"]
                        .search(
                            [
                                ("product_id", "in", product.product_variant_ids.ids),
                                ("state", "in", ["draft", "sent", "to approve"]),
                                ("approved_purchase", "=", True),
                            ]
                        )
                        .mapped("order_id")
                    )
                    order_ids._log_exception_activity_purchase(product)
