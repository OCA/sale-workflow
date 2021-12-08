# Copyright 2018 Tecnativa - Sergio Teruel
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).
from odoo import api, fields, models


class SaleOrderLine(models.Model):
    _inherit = "sale.order.line"

    discount = fields.Float(
        compute="_compute_discount",
        store=True,
        readonly=False,
    )

    @api.model_create_multi
    def create(self, vals_list):
        """Apply general discount for sale order lines which are not created
        from sale order form view.
        """
        for vals in vals_list:
            if "discount" not in vals and "order_id" in vals:
                sale_order = self.env["sale.order"].browse(vals["order_id"])
                if sale_order.general_discount:
                    product = self.env["product.product"].browse(vals["product_id"])
                    if product.general_discount_apply:
                        vals["discount"] = sale_order.general_discount
        return super().create(vals_list)

    @api.depends("order_id", "order_id.general_discount")
    def _compute_discount(self):
        if hasattr(super(), "_compute_discount"):
            super()._compute_discount()
        for line in self:
            if line.product_id.general_discount_apply:
                line.discount = line.order_id.general_discount

    @api.onchange("product_id")
    def _onchange_product_id(self):
        if hasattr(super(), "_onchange_product_id"):
            super()._onchange_product_id()
        for line in self:
            line.discount = 0
            if line.product_id.general_discount_apply:
                line.discount = line.order_id.general_discount
