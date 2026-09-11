# Copyright 2026 - TODAY, Kaynnan Lemes <kaynnan.lemes@escodoo.com.br>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

from odoo import api, fields, models


class BlanketOrderService(models.Model):
    _name = "blanket.order.service"
    _description = "Blanket Order Service Costs"

    blanket_order_id = fields.Many2one(
        "sale.blanket.order",
        string="Blanket Order Reference",
        required=True,
        ondelete="cascade",
        index=True,
        copy=False,
    )

    product_id = fields.Many2one(
        "product.product",
        string="Service",
    )
    quantity = fields.Float(
        default=1,
    )
    price_unit = fields.Float()
    subtotal = fields.Float(store=True, readonly=True, compute="_compute_subtotal")
    amount_total = fields.Float(
        store=True, readonly=True, compute="_compute_amount_total"
    )
    expected_date = fields.Datetime()

    @api.onchange("product_id", "quantity")
    def _onchange_product_id(self):
        for record in self:
            record.price_unit = self.product_id.standard_price
            record._compute_subtotal()

    @api.depends("product_id", "quantity", "price_unit")
    def _compute_subtotal(self):
        for record in self:
            record.subtotal = record.price_unit * record.quantity

    @api.depends("subtotal")
    def _compute_amount_total(self):
        for record in self:
            record.amount_total = record.subtotal
