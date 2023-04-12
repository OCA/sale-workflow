# Copyright 2015 Anybox S.A.S
# Copyright 2016-2018 Camptocamp SA
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).
from odoo import fields, models


class ProductSetLine(models.Model):
    _name = "product.set.line"
    _description = "Product set line"
    _rec_name = "product_id"
    _order = "sequence"

    product_id = fields.Many2one(
        comodel_name="product.product",
        domain=[("sale_ok", "=", True)],
        string="Product",
        required=True,
    )
    quantity = fields.Float(
        string="Quantity", digits="Product Unit of Measure", required=True, default=1.0
    )
    product_set_id = fields.Many2one("product.set", string="Set", ondelete="cascade")
    active = fields.Boolean(
        string="Active", related="product_set_id.active", store=True, readonly=True
    )
    sequence = fields.Integer(string="Sequence", required=True, default=0)
    discount = fields.Float(string="Discount (%)", digits="Discount", default=0.0)

    def prepare_sale_order_line_values(self, order, quantity, max_sequence=0):
        self.ensure_one()
        return {
            "order_id": order.id,
            "product_id": self.product_id.id,
            "product_uom_qty": self.quantity * quantity,
            "product_uom": self.product_id.uom_id.id,
            "sequence": max_sequence + self.sequence,
            "discount": self.discount,
            "company_id": order.company_id.id,
        }
