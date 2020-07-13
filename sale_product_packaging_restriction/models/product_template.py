# Copyright 2020 Camptocamp SA
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl)
from odoo import _, api, models
from odoo.exceptions import ValidationError


class ProductTemplate(models.Model):
    _inherit = "product.template"

    @api.constrains(
        "sell_only_by_packaging", "packaging_ids", "packaging_ids.can_be_sold"
    )
    def _check_sell_only_by_packaging_packaging_ids(self):
        res = super()._check_sell_only_by_packaging_packaging_ids()
        if not res:
            for product in self:
                if product.sell_only_by_packaging and not any(
                    pack.can_be_sold for pack in product.packaging_ids
                ):
                    raise ValidationError(
                        _(
                            "Product %s cannot be defined to be sold only by "
                            "packaging if it does not have any packaging that "
                            "can be sold defined."
                        )
                        % product.name
                    )
