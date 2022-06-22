# Copyright 2021 ACSONE SA/NV
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl)

from odoo import api, fields, models


class Rating(models.Model):
    _inherit = "rating.rating"

    purchase_verified = fields.Boolean(
        required=True, default=False, compute="_compute_purchase_verified", store=True
    )

    @api.depends("partner_id", "res_id", "res_model")
    def _compute_purchase_verified(self):
        partners = self.mapped("partner_id")
        product_ids = self.filtered(lambda r: r.res_model == "product.product").mapped(
            "res_id"
        )
        move_lines = self.env["account.move.line"].read_group(
            [
                ("move_id.payment_state", "=", "paid"),
                ("product_id", "in", product_ids),
                ("partner_id", "in", partners.ids),
            ],
            ["partner_id", "product_id"],
            ["partner_id", "product_id"],
            lazy=False,
        )
        partner_product_count = {}
        for line in move_lines:
            partner_product_count[
                (line["partner_id"][0], line["product_id"][0])
            ] = line["__count"]

        for record in self:
            record.purchase_verified = False
            purchased_product = (
                partner_product_count.get((record.partner_id.id, record.res_id), 0) > 0
            )
            if record.res_model == "product.product" and purchased_product:
                record.purchase_verified = True
