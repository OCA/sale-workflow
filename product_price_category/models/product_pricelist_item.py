# Copyright 2017 Camptocamp SA
# Copyright 2023 ACSONE SA/NV
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).


from odoo import _, api, fields, models


class ProductPricelistItem(models.Model):
    _inherit = "product.pricelist.item"

    applied_on = fields.Selection(
        selection_add=[("2b_product_price_category", "Price Category")],
        ondelete={"2b_product_price_category": "set default"},
    )
    display_applied_on = fields.Selection(
        selection_add=[("2b_product_price_category", "Price Category")],
        ondelete={"2b_product_price_category": "set default"},
    )
    price_category_id = fields.Many2one(
        comodel_name="product.price.category",
        string="Price Category",
        ondelete="cascade",
        help="Specify a product price category if this rule only applies "
        "to one price category. Keep empty otherwise.",
        compute="_compute_price_category",
        store=True,
        readonly=False,
    )

    def _compute_name(self):
        result = super()._compute_name()
        for item in self:
            if item.applied_on == "2b_product_price_category":
                item.name = _("Price Category: %s", item.price_category_id.display_name)
        return result

    @api.depends("display_applied_on")
    def _compute_price_category(self):
        """Reset the price_category_id value if applied_on
        is not price_category
        """
        for rec in self:
            if rec.display_applied_on != "2b_product_price_category":
                rec.applied_on = "2b_product_price_category"
                rec.price_category_id = False

    def _is_applicable_for(self, product, qty_in_product_uom):
        res = super()._is_applicable_for(product, qty_in_product_uom)
        if (
            self.price_category_id
            and self.price_category_id != product.price_category_id
        ):
            return False
        return res
