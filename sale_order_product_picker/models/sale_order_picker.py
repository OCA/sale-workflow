# Copyright 2023 Tecnativa - Sergio Teruel
# Copyright 2023 Tecnativa - Carlos Dauden
# License AGPL-3 - See https://www.gnu.org/licenses/agpl-3.0.html

from odoo import api, fields, models
from odoo.tools import float_compare


class SaleOrderPicker(models.Model):
    _name = "sale.order.picker"
    _description = "sale.order.picker"

    order_id = fields.Many2one(comodel_name="sale.order")
    product_id = fields.Many2one(comodel_name="product.product")
    product_image = fields.Image(related="product_id.image_256")
    sale_line_id = fields.Many2one(comodel_name="sale.order.line")
    is_in_order = fields.Boolean()
    product_uom_qty = fields.Float(string="Quantity", digits="Product Unit of Measure")
    uom_id = fields.Many2one(comodel_name="uom.uom", related="product_id.uom_id")
    unit_name = fields.Char(compute="_compute_unit_name")
    qty_available = fields.Float(
        string="On Hand",
        digits="Product Unit of Measure",
        compute="_compute_qty_available",
    )
    qty_delivered = fields.Float(string="Delivered", digits="Product Unit of Measure")
    times_delivered = fields.Integer()
    price_unit = fields.Float(
        string="Unit Price", compute="_compute_price_unit", digits="Product Price"
    )
    category_id = fields.Many2one("product.category", related="product_id.categ_id")
    currency_id = fields.Many2one(related="order_id.currency_id", depends=["order_id"])
    list_price = fields.Float(related="product_id.list_price")
    is_different_price = fields.Boolean(compute="_compute_is_different_price")

    def _get_picker_price_unit_context(self):
        return {
            "partner": self.order_id.partner_id,
            "pricelist": self.order_id.pricelist_id.id,
            "quantity": self.product_uom_qty,
        }

    @api.depends("product_id", "order_id.partner_id", "order_id.picker_price_origin")
    def _compute_price_unit(self):
        """
        Get product price unit from product list price or from last sale price
        """
        sale_order = fields.first(self).order_id
        price_origin = sale_order.picker_price_origin or "pricelist"
        use_delivery_address = sale_order.use_delivery_address
        for line in self:
            if price_origin == "last_sale_price":
                line.price_unit = line._get_last_sale_price_product(
                    use_delivery_address=use_delivery_address
                )
            else:
                line.price_unit = line.product_id.with_context(
                    **line._get_picker_price_unit_context()
                )._get_contextual_price()

    def _compute_qty_available(self):
        available_field = (
            self.env["ir.config_parameter"]
            .sudo()
            .get_param(
                "sale_order_product_picker.product_available_field", "qty_available"
            )
        )
        for line in self:
            line.qty_available = line.product_id[available_field]

    def _get_last_sale_price_product(self, use_delivery_address=False):
        """
        Get last price from last order.
        Use sudo to read sale order from other users like as other commercials.
        """
        self.ensure_one()
        domain = [
            ("company_id", "=", self.order_id.company_id.id),
            ("state", "not in", ("draft", "sent", "cancel")),
            ("product_id", "=", self.product_id.id),
        ]
        if use_delivery_address:
            domain.append(
                (
                    "order_id.partner_shipping_id",
                    "=",
                    self.order_id.partner_shipping_id.id,
                )
            )
        else:
            domain.append(("order_partner_id", "=", self.order_id.partner_id.id))
        so_line = (
            self.env["sale.order.line"]
            .sudo()
            .search(
                domain,
                limit=1,
                order="id DESC",
            )
            .with_context(prefetch_fields=False)
        )
        return so_line.price_unit or 0.0

    def add_to_cart(self):
        self.ensure_one()
        so_line = self.order_id.order_line.new({"product_id": self.product_id.id})
        so_line.product_id_change()
        self.order_id.order_line += so_line

    @api.depends("list_price", "price_unit")
    def _compute_is_different_price(self):
        digits = self.env["decimal.precision"].precision_get("Product Price")
        for line in self:
            line.is_different_price = bool(
                float_compare(line.price_unit, line.list_price, precision_digits=digits)
            )

    @api.depends("product_id")
    def _compute_unit_name(self):
        secondary_unit_installed = "sale_secondary_uom_id" in self.product_id._fields
        for line in self:
            if secondary_unit_installed and line.product_id.sale_secondary_uom_id:
                line.unit_name = line.product_id.sale_secondary_uom_id.display_name
            else:
                line.unit_name = line.product_id.uom_id.name
