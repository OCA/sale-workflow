# Copyright 2025 Moduon Team S.L.
# License LGPL-3.0 or later (https://www.gnu.org/licenses/lgpl-3.0)
from odoo import api, fields, models


class SaleOrder(models.Model):
    _inherit = "sale.order.line"

    origin_pricelist_item_id = fields.Many2one(
        comodel_name="product.pricelist.item",
        compute="_compute_origin_pricelist_item_id",
        help="Technical field to get the base pricelist item that has the origin "
        "price calculation",
    )
    price_locked = fields.Boolean(
        compute="_compute_price_locked",
        help="This flag will make the price_unit and discount readonly based on the "
        "pricelist locking criterias",
    )

    @api.depends("pricelist_item_id")
    def _compute_origin_pricelist_item_id(self):
        for line in self:
            # Just compute those items which price is pulled from another pricelist
            if (
                line.pricelist_item_id.base
                and line.pricelist_item_id.base == "pricelist"
                and line.pricelist_item_id.base_pricelist_id
            ):
                line.origin_pricelist_item_id = (
                    line.order_id.pricelist_id._get_base_product_rule(
                        line.product_id,
                        line.product_uom_qty or 1.0,
                        uom=line.product_uom,
                        date=line._get_order_date(),
                    )
                )
            else:
                line.origin_pricelist_item_id = line.pricelist_item_id

    @api.depends("origin_pricelist_item_id", "pricelist_item_id")
    def _compute_price_locked(self):
        self.price_locked = False
        # Sales manager are able to change pricelists so they shouldn't be block
        if self.env.user.has_group("sales_team.group_sale_manager"):
            return
        self.filtered(
            lambda x: (
                x.origin_pricelist_item_id
                and x.pricelist_item_id.pricelist_id.lock_product_prices_applied_on
                and (
                    x.origin_pricelist_item_id.applied_on
                    <= x.pricelist_item_id.pricelist_id.lock_product_prices_applied_on
                )
            )
            or (
                not x.origin_pricelist_item_id
                and x.pricelist_item_id.pricelist_id.lock_product_prices_applied_on
                == "3_global"
            )
        ).price_locked = True
