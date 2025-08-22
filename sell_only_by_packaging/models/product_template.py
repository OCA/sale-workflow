# Copyright 2020 Camptocamp SA
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl)

from odoo import api, fields, models
from odoo.exceptions import ValidationError


class ProductTemplate(models.Model):
    _inherit = "product.template"

    sell_only_by_packaging = fields.Boolean(
        string="Only sell by packaging",
        company_dependent=True,
        default=False,
        help="Restrict the usage of this product on sale order lines without "
        "packaging defined",
        copy=False,
    )

    min_sellable_qty = fields.Float(
        compute="_compute_template_min_sellable_qty",
        help=(
            "Minimum sellable quantity, according to the available packagings, "
            "if Only Sell by Packaging is set."
        ),
    )

    @api.depends(
        "sell_only_by_packaging",
        "uom_id.factor",
        "product_variant_ids.min_sellable_qty",
    )
    def _compute_template_min_sellable_qty(self):
        for record in self:
            record.min_sellable_qty = 0.0
            if len(record.product_variant_ids) == 1:
                # Pick the value from the variant if there's only 1
                record.min_sellable_qty = record.product_variant_ids.min_sellable_qty

    @api.constrains("sell_only_by_packaging", "sale_ok")
    def _check_sell_only_by_packaging_sale_ok(self):
        for product in self:
            if product.sell_only_by_packaging and not product.sale_ok:
                raise ValidationError(
                    self.env._(
                        "Product %s cannot be defined to be sold only by "
                        "packaging if it cannot be sold.",
                        product.name,
                    ),
                )

    @api.constrains("sell_only_by_packaging", "packaging_ids")
    def _check_sell_only_by_packaging_can_be_sold_packaging_ids(self):
        for product in self:
            if product.sell_only_by_packaging:
                if (
                    # Product template only condition
                    len(product.product_variant_ids) == 1
                    and not any(pack.sales for pack in product.packaging_ids)
                    # Product variants condition
                    or len(product.product_variant_ids) > 1
                    and not any(
                        pack.sales
                        for pack in product.product_variant_ids.mapped("packaging_ids")
                    )
                ):
                    raise ValidationError(
                        self.env._(
                            "Product %s cannot be defined to be sold only by "
                            "packaging if it does not have any packaging that "
                            "can be sold defined.",
                            product.name,
                        ),
                    )

    @api.depends("sale_ok")
    def _compute_expense_policy(self):
        self.filtered(
            lambda t: not t.sale_ok and t.sell_only_by_packaging
        ).sell_only_by_packaging = False
        return super()._compute_expense_policy()
