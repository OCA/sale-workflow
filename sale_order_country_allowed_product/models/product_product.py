# Copyright 2025 Manuel Regidor <manuel.regidor@sygel.es>
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).

from odoo import api, models
from odoo.osv import expression


class ProductProduct(models.Model):
    _inherit = "product.product"

    @api.model
    def _search(self, domain, offset=0, limit=None, order=None):
        # ORM reads (fetch) search by ids and must not be filtered
        is_id_lookup = (
            isinstance(domain, list)
            and len(domain) == 1
            and isinstance(domain[0], tuple | list)
            and domain[0][0] == "id"
            and domain[0][1] == "in"
        )
        if (
            self.env.context.get("restrict_by_country", False) and not is_id_lookup
        ) and not self.env.user.has_group(
            "sale_order_country_allowed_product.ignore_country_sale"
        ):
            partner = self.env["res.partner"].search(
                [("id", "=", self.env.context.get("restrict_by_country_partner_id"))],
                limit=1,
            )
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
        return super()._search(domain, offset=offset, limit=limit, order=order)
