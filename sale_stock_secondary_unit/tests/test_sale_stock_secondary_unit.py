# Copyright 2019 Tecnativa - Sergio Teruel
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).
from odoo.tests import Form, TransactionCase, tagged


@tagged("post_install", "-at_install")
class TestSaleStockOrderSecondaryUnit(TransactionCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.warehouse = cls.env.ref("stock.warehouse0")
        cls.product_uom_kg = cls.env.ref("uom.product_uom_kgm")
        cls.product_uom_gram = cls.env.ref("uom.product_uom_gram")
        cls.product_uom_unit = cls.env.ref("uom.product_uom_unit")
        cls.product = cls.env["product.product"].create(
            {
                "name": "test",
                "type": "product",
                "uom_id": cls.product_uom_kg.id,
                "uom_po_id": cls.product_uom_kg.id,
            }
        )
        # Set secondary uom on product template
        cls.product.product_tmpl_id.write(
            {
                "secondary_uom_ids": [
                    (
                        0,
                        0,
                        {
                            "name": "unit-700",
                            "uom_id": cls.product_uom_unit.id,
                            "factor": 0.7,
                        },
                    )
                ],
            }
        )
        StockQuant = cls.env["stock.quant"]
        StockQuant.create(
            {
                "product_id": cls.product.id,
                "location_id": cls.warehouse.lot_stock_id.id,
                "quantity": 2000,
            }
        )
        cls.secondary_unit = cls.env["product.secondary.unit"].search(
            [("product_tmpl_id", "=", cls.product.product_tmpl_id.id)]
        )
        cls.product.sale_secondary_uom_id = cls.secondary_unit.id
        cls.partner = cls.env["res.partner"].create({"name": "test - partner"})
        so_f = Form(cls.env["sale.order"])
        so_f.partner_id = cls.partner
        so_f.pricelist_id = cls.env.ref("product.list0")
        with so_f.order_line.new() as sol_f:
            sol_f.name = cls.product.name
            sol_f.product_id = cls.product
            sol_f.product_uom_qty = 1
            sol_f.product_uom = cls.product.uom_id
            sol_f.price_unit = 1000.00
        cls.order = so_f.save()

    def test_stock_move_line_secondary_unit(self):
        with Form(self.order) as so_f:
            with so_f.order_line.edit(0) as sol_f:
                sol_f.secondary_uom_id = self.secondary_unit
                sol_f.secondary_uom_qty = 5
        self.order.action_confirm()
        picking = self.order.picking_ids
        self.assertEqual(picking.move_ids.secondary_uom_qty, 5.0)
