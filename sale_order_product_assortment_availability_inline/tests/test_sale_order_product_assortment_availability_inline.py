# Copyright 2022 Tecnativa - Sergio Teruel
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).

from odoo.tests import Form, SavepointCase, tagged


@tagged("post_install", "-at_install")
class TestSaleOrderProductAssortmentAvailabilityInline(SavepointCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.partner = cls.env["res.partner"].create({"name": "Partner"})
        cls.product = cls.env["product.product"].create(
            {"name": "Product", "type": "product"}
        )
        cls.warehouse1 = cls.env["stock.warehouse"].create(
            {"name": "Warehouse 1", "code": "AI1"}
        )
        StockQuant = cls.env["stock.quant"]
        StockQuant.create(
            {
                "product_id": cls.product.id,
                "product_uom_id": cls.product.uom_id.id,
                "location_id": cls.warehouse1.lot_stock_id.id,
                "quantity": 10.00,
            }
        )

    def test_sale_order_product_rec_name(self):
        self.env.ref("product.decimal_product_uom").write({"digits": 3})
        so_form = Form(
            self.env["sale.order"].with_context(
                warehouse=self.warehouse1.id, so_product_stock_inline=True
            )
        )
        so_form.partner_id = self.partner
        with so_form.order_line.new() as line_form:
            line_form.product_id = self.product
            self.assertTrue(
                line_form.product_id.display_name.endswith("(10.000 Units)")
            )
