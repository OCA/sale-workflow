# Copyright 2024 Camptocamp SA
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).

from odoo.tests import Form, common

from odoo.addons.base.tests.common import DISABLED_MAIL_CONTEXT


class TestSaleStockPartnerWarehouse(common.TransactionCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.env = cls.env["base"].with_context(**DISABLED_MAIL_CONTEXT).env
        cls.warehouse_1 = cls.env["stock.warehouse"].create(
            {
                "name": "Base Warehouse",
                "reception_steps": "one_step",
                "delivery_steps": "ship_only",
                "code": "BWH",
            }
        )
        cls.warehouse_2 = cls.env["stock.warehouse"].create(
            {
                "name": "Test Warehouse",
                "reception_steps": "one_step",
                "delivery_steps": "ship_only",
                "code": "TWH",
            }
        )
        cls.partner = cls.env["res.partner"].create(
            {"name": "Test Customer", "email": "customer@test.com"}
        )
        cls.shipping_partner = cls.env["res.partner"].create(
            {
                "name": "Test Shipping Address",
                "parent_id": cls.partner.id,
                "type": "delivery",
            }
        )

    def test_sale_stock_partner_warehouse(self):
        with Form(self.env["sale.order"]) as order_form:
            order_form.partner_id = self.partner
        order = order_form.save()
        self.assertNotEqual(order.warehouse_id, self.warehouse_1)
        self.partner.sale_warehouse_id = self.warehouse_1
        self.shipping_partner.sale_warehouse_id = self.warehouse_2
        order._compute_warehouse_id()
        self.assertEqual(order.warehouse_id, self.warehouse_1)
        order.partner_shipping_id = self.shipping_partner
        self.assertEqual(order.warehouse_id, self.warehouse_1)
        order.company_id.sale_warehouse_by_partner_shipping = True
        order._compute_warehouse_id()
        self.assertEqual(order.warehouse_id, self.warehouse_2)
