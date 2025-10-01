# Copyright 2025 Manuel Regidor <manuel.regidor@sygel.es>
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).

from odoo import api, models
from odoo.osv import expression


class ProductProduct(models.Model):
    _inherit = "product.product"

    @api.model
    def _search(
        self,
        args,
        offset=0,
        limit=None,
        order=None,
        count=False,
        access_rights_uid=None,
    ):
        if self.env.context.get(
            "restrict_by_country", False
        ) and not self.env.user.has_group(
            "sale_order_country_allowed_product.ignore_country_sale"
        ):
            partner = self.env["res.partner"].search(
                [("id", "=", self.env.context.get("restrict_by_country_partner_id"))],
                limit=1,
            )
            if partner.country_id:
                args = expression.AND(
                    [
                        args,
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
            args,
            offset=offset,
            limit=limit,
            order=order,
            count=count,
            access_rights_uid=access_rights_uid,
        )
