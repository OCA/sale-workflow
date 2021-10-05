# Copyright 2021 Camptocamp SA
# @author Simone Orsi <simone.orsi@camptocamp.com>
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl)
from odoo import _, api, exceptions, fields, models


class ProductSetLine(models.Model):
    _inherit = "product.set.line"

    # Just for UI purpose
    sell_only_by_packaging = fields.Boolean(related="product_id.sell_only_by_packaging")

    @api.constrains("product_id.sell_only_by_packaging", "product_packaging_id")
    def _check_sell_only_by_packaging(self):
        errored = self.filtered(
            lambda x: x.product_id.sell_only_by_packaging and not x.product_packaging_id
        )
        if errored:
            raise exceptions.UserError(
                self._check_sell_only_by_packaging_err_msg(errored)
            )

    def _check_sell_only_by_packaging_err_msg(self, lines):
        return _(
            "The following product(s) can be sold only by packaging: \n   %s"
        ) % ", ".join(lines.mapped("product_id.display_name"))
