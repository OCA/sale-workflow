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
                    product = self.env["product.product"].browse(
                        vals.get("product_id", False)
                    )
                    if product and product.general_discount_apply:
                        vals["discount"] = sale_order.general_discount
        return super().create(vals_list)

    @api.depends("order_id", "order_id.general_discount")
    def _compute_discount(self):
        res = super()._compute_discount()
        for line in self:
            # We check the value of general_discount on origin too to cover
            # the case where a discount was set to a value != 0 and then
            # set again to 0 to remove the discount on all the lines at the same
            # time
            if line.product_id.general_discount_apply and (
                line.order_id.general_discount or line.order_id._origin.general_discount
            ):
                line.discount = line.order_id.general_discount
            else:
                line.discount = 0
        return res
