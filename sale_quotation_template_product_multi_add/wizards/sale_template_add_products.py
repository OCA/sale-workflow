from odoo import api, fields, models


class SaleTemplateAddProducts(models.TransientModel):
    _name = "sale.template.add.products"
    _description = "Quotation Template Add Products"

    product_ids = fields.Many2many(comodel_name="product.product")
    item_ids = fields.One2many(
        comodel_name="sale.template.add.products.item",
        inverse_name="wizard_id",
    )

    def create_items(self):
        for wizard in self:
            vals_list = [
                {"product_id": r.id, "wizard_id": wizard.id} for r in wizard.product_ids
            ]
            self.env["sale.template.add.products.item"].create(vals_list)
        view = self.env.ref(
            "sale_quotation_template_product_multi_add.view_add_products_to_qt2"
        )
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
    def _get_line_values(self, qt, item):
        sale_line = self.env["sale.order.template.line"].new(
            {
                "sale_order_template_id": qt.id,
                "name": item.name or item.product_id.name,
                "product_id": item.product_id.id,
                "product_uom_qty": item.quantity,
                "product_uom_id": item.product_id.uom_id.id,
            }
        )
        line_values = sale_line._convert_to_write(sale_line._cache)
        return line_values

    def select_products(self):
        qt_obj = self.env["sale.order.template"]
        for wizard in self:
            qt = qt_obj.browse(self.env.context.get("active_id", False))
            if qt:
                for item in wizard.item_ids:
                    vals = self._get_line_values(qt, item)
                    if vals:
                        self.env["sale.order.template.line"].create(vals)
        return {"type": "ir.actions.act_window_close"}


class SaleTemplateAddProductsItem(models.TransientModel):
    _name = "sale.template.add.products.item"
    _description = "Quotation Template Add Products Item"

    name = fields.Char("Description")
    wizard_id = fields.Many2one(
        string="Wizard", comodel_name="sale.template.add.products"
    )
    product_id = fields.Many2one(
        string="Product", comodel_name="product.product", required=True
    )
    quantity = fields.Float(
        digits="Product Unit of Measure", default=1.0, required=True
    )
