# Copyright 2020 Camptocamp SA
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl)
from odoo import _, api, fields, models
from odoo.exceptions import ValidationError


class ProductTemplate(models.Model):
    _inherit = "product.template"

    sell_only_by_packaging = fields.Boolean(
        string="Only sell by packaging",
        default=False,
        help="Restrict the usage of this product on sale order lines without "
        "packaging defined",
    )

    @api.constrains("sell_only_by_packaging", "sale_ok", "packaging_ids")
    def _check_sell_only_by_packaging_sale_ok(self):
        for product in self:
            if product.sell_only_by_packaging and not product.sale_ok:
                raise ValidationError(
                    _(
                        "Product %s cannot be defined to be sold only by "
                        "packaging if it cannot be sold."
                    )
                    % product.name
                )

    @api.constrains("sell_only_by_packaging", "packaging_ids")
    def _check_sell_only_by_packaging_packaging_ids(self):
        for product in self:
            if product.sell_only_by_packaging and not product.packaging_ids:
                raise ValidationError(
                    _(
                        "Product %s cannot be defined to be sold only by "
                        "packaging if it does not have any packaging defined."
                    )
                    % product.name
                )

    @api.constrains(
        "sell_only_by_packaging", "packaging_ids", "packaging_ids.can_be_sold"
    )
    def _check_sell_only_by_packaging_can_be_sold_packaging_ids(self):
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

    @api.onchange("sale_ok")
    def _change_sale_ok(self):
        if not self.sale_ok and self.sell_only_by_packaging:
            self.sell_only_by_packaging = False
        return super()._change_sale_ok()
