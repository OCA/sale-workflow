# Copyright 2025 Manuel Regidor <manuel.regidor@sygel.es>
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).

from odoo import api, models
from odoo.osv import expression


class ProductProduct(models.Model):
    _inherit = "product.product"

    @api.model
    def _search(
        self,
        domain,
        offset=0,
        limit=None,
        order=None,
    ):
        if self.env.context.get(
            "restrict_by_country", False
        ) and not self.env.user.has_group(
            "sale_order_country_allowed_product.ignore_country_sale"
        ):
            partner_id =self.env.context.get("restrict_by_country_partner_id")
            partner = self.env["res.partner"].browse(partner_id) if partner_id else self.env["res.partner"]
            if partner.country_id:
                domain = expression.AND(
                    [
                        domain,
                        [
                            "|",
                            ("product_tmpl_id.sale_allowed_country_ids", "=", False),
                            (
                                "product_tmpl_id.sale_allowed_country_ids",
                                "in",
                                [partner.country_id.id],
                            ),
                        ],
                    ]
                )
        return super()._search(
            domain,
            offset=offset,
            limit=limit,
            order=order,
        )
