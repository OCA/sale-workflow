# Copyright 2017 Camptocamp SA
# Copyright 2023 ACSONE SA/NV
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).


from odoo import models


class ProductPricelist(models.Model):
    _inherit = "product.pricelist"

    def _get_applicable_rules_domain(self, products, date, **kwargs):
        price_categ_ids = [
            p.price_category_id.id for p in products if p.price_category_id
        ]
        domain = super()._get_applicable_rules_domain(products, date, **kwargs)
        if price_categ_ids:
            domain.extend(
                [
                    "|",
                    ("price_category_id", "=", False),
                    ("price_category_id", "in", price_categ_ids),
                ]
            )
        return domain
