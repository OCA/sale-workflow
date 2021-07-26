# Copyright (C) 2021 - TODAY, Open Source Integrators
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo import api, fields, models


class SaleOrderLineFromStock(models.TransientModel):
    _name = "sale.order.line.from_stock"
    _description = "Sale Line from Stock"

    sale_id = fields.Many2one("sale.order", string="Sale Order")
    product_tmpl_id = fields.Many2one("product.template", string="Product Template")
    value_ids = fields.Many2many(
        "product.attribute.value", string="Required Attribute Values"
    )
    serial_list = fields.Text(string="Serial List")
    quant_ids = fields.Many2many("stock.quant", string="Quants", readonly=False)
    list_limit = fields.Integer(string="Search Limit", default=10)

    @api.onchange("product_tmpl_id", "serial_list", "value_ids", "list_limit")
    def onchange_quant_ids(self):
        self.ensure_one()
        if not self.product_tmpl_id:
            self.quant_ids = False
            self.value_ids = False
        else:
            domain = [
                ("location_id.usage", "=", "internal"),
                ("quantity", ">", 0.0),
                ("reserved_quantity", "=", 0.0),
                ("product_id", "in", self.product_tmpl_id.product_variant_ids.ids),
            ]
            for value in self.value_ids:
                domain.append(
                    ("product_id.product_template_attribute_value_ids", "in", value.ids)
                )
            if self.serial_list:
                domain.append(("lot_id.name", "in", self.serial_list.split("\n")))
            self.quant_ids = self.env["stock.quant"].search(
                domain, limit=self.list_limit
            )

    def add(self):
        self.ensure_one()
        route_from_stock = self.env.ref("sale_order_serial.route_from_stock")
        self = self.with_context(
            skip_existing_serials_check=1, skip_existing_soline_check=1
        )
        self.sale_id.write(
            {
                "order_line": [
                    (
                        0,
                        0,
                        {
                            "route_id": route_from_stock.id,
                            "product_id": q.product_id.id,
                            "serial_list": q.lot_id.name,
                            "product_uom_qty": q.quantity,
                        },
                    )
                    for q in self.quant_ids
                ]
            }
        )
        return True
