# Copyright 2024 Akretion (https://www.akretion.com).
# @author Kévin Roche <kevin.roche@akretion.com>
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).

from odoo.tests import TransactionCase

from odoo.addons.base.tests.common import DISABLED_MAIL_CONTEXT


class TestSaleOrderLineDisplayStockPerWarehouse(TransactionCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.env = cls.env(context=dict(cls.env.context, **DISABLED_MAIL_CONTEXT))
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
                "type": "consu",
                "is_storable": True,
            }
        )
        cls.service_product = cls.env["product.product"].create(
            {
                "name": "Test Service",
                "type": "service",
            }
        )

        cls.env["stock.quant"]._update_available_quantity(
            cls.product,
            cls.warehouse_1.lot_stock_id,
            11,
        )

        cls.env["stock.quant"]._update_available_quantity(
            cls.product,
            cls.warehouse_2.lot_stock_id,
            22,
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
                    ),
                    (
                        0,
                        0,
                        {
                            "product_id": cls.service_product.id,
                            "product_uom_qty": 1,
                        },
                    ),
                ],
            }
        )

        cls.sale_order_line = cls.sale_order.order_line[0]
        cls.service_order_line = cls.sale_order.order_line[1]

    def test_display_widget_only_for_storable_products(self):
        self.assertTrue(self.sale_order_line.display_qty_per_warehouse_widget)
        self.assertFalse(self.service_order_line.display_qty_per_warehouse_widget)

    def test_qty_per_warehouse_widget_data_empty_for_non_storable_product(self):
        self.assertEqual(self.service_order_line.qty_per_warehouse_widget_data, [])

    def test_one_stock_per_warehouse_info(self):
        data = self.sale_order_line.qty_per_warehouse_widget_data
        self.assertEqual(
            data[self.warehouse_1.id]["warehouse_name"],
            self.warehouse_1.display_name,
        )
        self.assertEqual(data[self.warehouse_1.id]["qty"], 11.0)
        self.assertNotIn(self.warehouse_2.id, data)

    def test_two_stock_per_warehouse_info(self):
        self.warehouse_2.display_stock_on_sol = True
        data = self.sale_order_line.qty_per_warehouse_widget_data
        self.assertEqual(data[self.warehouse_1.id]["qty"], 11.0)
        self.assertEqual(data[self.warehouse_2.id]["qty"], 22.0)

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
        data = self.sale_order_line.qty_per_warehouse_widget_data
        self.assertEqual(data[self.warehouse_1.id]["qty"], 11.0)
        self.assertEqual(data[self.warehouse_3.id]["qty"], 0)

    def test_stock_field_setting_virtual_available(self):
        move = self.env["stock.move"].create(
            {
                "name": "Incoming",
                "product_id": self.product.id,
                "product_uom": self.product.uom_id.id,
                "product_uom_qty": 5,
                "location_id": self.env.ref("stock.stock_location_suppliers").id,
                "location_dest_id": self.warehouse_1.lot_stock_id.id,
            }
        )
        move._action_confirm()
        self.env["ir.config_parameter"].sudo().set_param(
            "sale_order_line_stock_info.stock_field_on_sol", "virtual_available"
        )
        self.sale_order_line.invalidate_recordset(["qty_per_warehouse_widget_data"])
        data = self.sale_order_line.qty_per_warehouse_widget_data
        self.assertEqual(data[self.warehouse_1.id]["qty"], 16.0)
        self.env["ir.config_parameter"].sudo().set_param(
            "sale_order_line_stock_info.stock_field_on_sol", "qty_available"
        )
        self.sale_order_line.invalidate_recordset(["qty_per_warehouse_widget_data"])
        data = self.sale_order_line.qty_per_warehouse_widget_data
        self.assertEqual(data[self.warehouse_1.id]["qty"], 11.0)
