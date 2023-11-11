# Copyright 2016 Cédric Pigeon, ACSONE SA/NV (<http://acsone.eu>)
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

from odoo import api, fields, models


class SaleImportProducts(models.TransientModel):
    _name = "sale.import.products"
    _description = "Sale Import Products"

    products = fields.Many2many(comodel_name="product.product")
    items = fields.One2many(
        comodel_name="sale.import.products.items",
        inverse_name="wizard_id",
    )

    def create_items(self):
        for wizard in self:
            for product in wizard.products:
                self.env["sale.import.products.items"].create(
                    {"wizard_id": wizard.id, "product_id": product.id}
                )
        view = self.env.ref("sale_product_multi_add.view_import_product_to_sale2")
        return {
            "type": "ir.actions.act_window",
            "res_model": self._name,
            "view_type": "form",
            "view_mode": "form",
            "views": [(view.id, "form")],
            "target": "new",
            "res_id": self.id,
            "context": self.env.context,
        }

    @api.model
    def _get_line_values(self, sale, item):
        sale_line = self.env["sale.order.line"].new(
            {
                "order_id": sale.id,
                "name": item.product_id.name,
                "product_id": item.product_id.id,
                "product_uom_qty": item.quantity,
                "product_uom": item.product_id.uom_id.id,
                "price_unit": item.product_id.list_price,
            }
        )
        line_values = sale_line._convert_to_write(sale_line._cache)
        return line_values

    def select_products(self):
        so_obj = self.env["sale.order"]
        for wizard in self:
            sale = so_obj.browse(self.env.context.get("active_id", False))

            if sale:
                for item in wizard.items:
                    vals = self._get_line_values(sale, item)
                    if vals:
                        self.env["sale.order.line"].create(vals)

        return {"type": "ir.actions.act_window_close"}


class SaleImportProductsItem(models.TransientModel):
    _name = "sale.import.products.items"
    _description = "Sale Import Products Items"

    wizard_id = fields.Many2one(string="Wizard", comodel_name="sale.import.products")
    product_id = fields.Many2one(
        string="Product", comodel_name="product.product", required=True
    )
    quantity = fields.Float(
        digits="Product Unit of Measure", default=1.0, required=True
    )
