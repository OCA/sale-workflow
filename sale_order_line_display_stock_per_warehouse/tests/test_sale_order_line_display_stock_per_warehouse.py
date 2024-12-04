# Copyright 2024 Akretion (https://www.akretion.com).
# @author Kévin Roche <kevin.roche@akretion.com>
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).

from odoo.tests.common import SavepointCase


class TestSaleOrderLineDisplayStockPerWarehouse(SavepointCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.company = cls.env.ref("base.main_company")

        cls.warehouse_1 = cls.env["stock.warehouse"].create(
            {
                "name": "WH1",
                "code": "WH1",
                "company_id": cls.company.id,
                "display_stock_on_sol": True,
            }
        )
        cls.warehouse_2 = cls.env["stock.warehouse"].create(
            {
                "name": "WH2",
                "code": "WH2",
                "company_id": cls.company.id,
                "display_stock_on_sol": False,
            }
        )

        cls.product = cls.env["product.product"].create(
            {
                "name": "Test Product",
                "type": "product",
            }
        )

        cls.env["stock.quant"].create(
            {
                "product_id": cls.product.id,
                "location_id": cls.warehouse_1.lot_stock_id.id,
                "quantity": 11,
            }
        )
        cls.env["stock.quant"].create(
            {
                "product_id": cls.product.id,
                "location_id": cls.warehouse_2.lot_stock_id.id,
                "quantity": 22,
            }
        )

        cls.sale_order = cls.env["sale.order"].create(
            {
                "partner_id": cls.env.ref("base.res_partner_1").id,
                "company_id": cls.company.id,
                "order_line": [
                    (
                        0,
                        0,
                        {
                            "product_id": cls.product.id,
                            "product_uom_qty": 1,
                        },
                    )
                ],
            }
        )

        cls.sale_order_line = cls.sale_order.order_line

    def test_one_stock_per_warehouse_info(self):
        self.assertIn("WH1: 11.0", self.sale_order_line.stock_per_warehouse_info)
        self.assertNotIn("WH1: 22.0", self.sale_order_line.stock_per_warehouse_info)

    def test_two_stock_per_warehouse_info(self):
        self.warehouse_2.display_stock_on_sol = True
        self.assertIn("WH1: 11.0", self.sale_order_line.stock_per_warehouse_info)
        self.assertIn("WH2: 22.0", self.sale_order_line.stock_per_warehouse_info)

    def test_third_stock_per_warehouse_info_with_zero_stock(self):
        self.warehouse_3 = self.env["stock.warehouse"].create(
            {
                "name": "WH3",
                "code": "WH3",
                "company_id": self.company.id,
                "display_stock_on_sol": True,
            }
        )
        self.env["stock.quant"].create(
            {
                "product_id": self.product.id,
                "location_id": self.warehouse_3.lot_stock_id.id,
                "quantity": 0,
            }
        )
        self.assertIn("WH1: 11.0", self.sale_order_line.stock_per_warehouse_info)
        self.assertIn("WH3: 0", self.sale_order_line.stock_per_warehouse_info)
