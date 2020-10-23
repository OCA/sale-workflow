# Copyright 2020 ACSONE SA/NV
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo import _, api, fields, models
from odoo.exceptions import ValidationError


class ProductPriceList(models.Model):
    """Allow to use a subset of pricelists to be used as tier definitions,
       and provides the method to compute a price based on these tiers.
    """

    _inherit = "product.pricelist"

    is_tiered_pricing = fields.Boolean()
    tier_items = fields.One2many("product.pricelist.item", compute="_compute_tiers")

    def name_get(self):
        """Append the tier description to tiered pricings."""
        res = super(ProductPriceList, self).name_get()
        prefixes = self.display_tiers()
        return [(r[0], p + r[1]) for p, r in zip(prefixes, res)]

    def display_tiers(self, one=False):
        """Return a string representation of tiers.
           It returns them as a list, unless one is True, in which case it directly
           returns the string.
        """
        prefixes = []
        for pricelist in self:
            prefix = ""
            if pricelist.is_tiered_pricing:
                items = pricelist.tier_items
                items_str = "|".join(
                    _("{}/{}").format(i.min_quantity, i.price) for i in items
                )
                prefix = _("[Tiers:{}] ").format(items_str)
            prefixes.append(prefix)
        if one:
            self.ensure_one()
            return prefixes[0]
        else:
            return prefixes

    def _compute_tiers(self):
        for price_list in self:
            if price_list.is_tiered_pricing:
                price_list.tier_items = price_list.item_ids.sorted("min_quantity")
            else:
                price_list.tier_items = False

    def split_quantity_by_tiers(self, quantity):
        """Returns a list of the quantities for each reached tier.
           So if we have tiers 0, 100, 200, and split 250, we get [100, 100, 50].
           By splitting 111 we get [100, 11].
        """
        self.ensure_one()
        assert self.is_tiered_pricing
        result = []
        previous = 0
        for tier in self.tier_items[1:]:  # we always have a first tier
            tier_quantity = tier.min_quantity
            difference = tier_quantity - previous
            if quantity > difference:
                quantity -= difference
                previous = tier_quantity
                result.append(difference)
        if quantity:
            result.append(quantity)
        return result

    def get_quantities_and_prices(self, price, price_uom, product, quantity):
        """Returns a list of the quantities/price tuples for each reached tier.
           So if we have tiers 0, 100, 200:
           by splitting 250, we get [(100, x), (100, y), (50, z)].
           by splitting 111, we get [(100, x), (111, y)].
           It's allowed to use formulas for tiers, so the prices can vary.
        """
        self.ensure_one()
        assert self.is_tiered_pricing
        quantities = self.split_quantity_by_tiers(quantity)
        prices = [
            i._compute_price(price, price_uom, product, quantity)
            for i in self.tier_items
        ]
        return list(zip(quantities, prices))

    @api.constrains("item_ids")
    def _constrains_tier_items(self):
        """A tier item is uniquely defined by quantity and price.
           These should form tiers (an ordered sequence)
           We don't constrain the unused fields, but simply clean them.
        """
        tiered_pricings = self.filtered("is_tiered_pricing")
        recursive_tiers = tiered_pricings.filtered(
            lambda t: "tier" in t.mapped("item_ids.compute_price")
        )
        if recursive_tiers:
            message = _(
                "You cannot have recursive tiered pricings. "
                "Check the following pricelists:"
            )
            names = ", ".join(n for n in recursive_tiers.mapped("names") if n)
            raise ValidationError(_("{}\n{}").format(message, names))  # yeah...
        for price_list in tiered_pricings:
            if not price_list.item_ids:
                raise ValidationError(_("No tier lines."))
            quantities = price_list.mapped("item_ids.min_quantity")
            if 0 not in quantities:
                raise ValidationError(_("The first tier should start at zero."))
            if any(q < 0 for q in quantities):
                raise ValidationError(_("An item has a negative a minimum quantity."))
            if len(quantities) != len(set(quantities)):
                raise ValidationError(_("All tiers should be different."))

        tiered_pricings._clean_tier_items()

    def _clean_tier_items(self):
        """A tier item is uniquely defined by quantity and price.
           Therefore all other fields are unused; to make things cleaner,
           we force the values to be the one that will be applied anyway.
        """
        tiered_pricings = self.filtered("is_tiered_pricing")
        unused_fields = [
            "product_tmpl_id",
            "product_id",
            "categ_id",
            "base_pricelist_id",
            "date_start",
            "date_end",
        ]
        items_to_clean = tiered_pricings.mapped("item_ids")
        for item in items_to_clean:
            for field in unused_fields:
                item[field] = False
            item["applied_on"] = "3_global"
            item["base"] = "list_price"

    def is_tier_priced_sale_line(self, product, sale_order_line):
        """ :return: boolean: is a tier pricing used in computing this line's price
        """
        self.ensure_one()
        return bool(self.get_tier_rule(product, sale_order_line))

    def get_tier_rule(self, product, sale_order_line):
        """ :return: "product.pricelist.item"
            return a tier pricing rule used in computing this line's price, if any
        """
        self.ensure_one()
        no_item = self.env["product.pricelist.item"]
        quantity = sale_order_line.product_uom_qty
        partner = sale_order_line.order_id.partner_id
        price, item_id = self.get_product_price_rule(product, quantity, partner)
        item = no_item.browse(item_id)
        if item.compute_price in ["tier", "volume"]:
            return item
        elif item.base != "pricelist":
            return no_item
        else:
            base = item.base_pricelist_id
            return base.is_tier_priced_sale_line(product, sale_order_line)
