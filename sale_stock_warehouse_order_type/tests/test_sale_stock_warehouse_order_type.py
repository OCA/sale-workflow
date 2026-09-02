# Copyright 2025 Tecnativa - Eduardo Ezerouali
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl)
from odoo import Command
from odoo.tests import tagged

from odoo.addons.base.tests.common import BaseCommon


@tagged("post_install", "-at_install")
class TestSaleStockWarehouseOrderType(BaseCommon):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.company = cls.env.ref("base.main_company")
        Warehouse = cls.env["stock.warehouse"].with_context(tracking_disable=True)
        cls.warehouse_partner = Warehouse.create(
            {
                "name": "Warehouse 1 - Partner",
                "code": "WH-1",
                "company_id": cls.company.id,
            }
        )
        cls.warehouse_shipping = Warehouse.create(
            {
                "name": "Warehouse 2 - Partner Shipping",
                "code": "WH-2",
                "company_id": cls.company.id,
            }
        )
        cls.warehouse_user = Warehouse.create(
            {
                "name": "Warehouse 3 - User/Comercial",
                "code": "WH-3",
                "company_id": cls.company.id,
            }
        )
        cls.warehouse_type = Warehouse.create(
            {
                "name": "Warehouse 4 - Sale Order Type",
                "code": "WH-4",
                "company_id": cls.company.id,
            }
        )
        cls.sale_order_type = cls.env["sale.order.type"].create(
            {"name": "Test Type", "warehouse_id": cls.warehouse_type.id}
        )
        Partner = cls.env["res.partner"]
        cls.partner = Partner.create(
            {"name": "Test Partner", "company_id": cls.company.id}
        )
        cls.partner.sale_warehouse_id = cls.warehouse_partner
        cls.partner_shipping = Partner.create(
            {
                "name": "Test Partner - Shipping",
                "type": "delivery",
                "parent_id": cls.partner.id,
                "company_id": cls.company.id,
            }
        )
        cls.partner_shipping.sale_warehouse_id = cls.warehouse_shipping
        Users = cls.env["res.users"].with_context(tracking_disable=True)
        cls.user = Users.create(
            {
                "name": "Test User",
                "login": "test_user@example.com",
                "company_id": cls.company.id,
                "company_ids": [Command.set([cls.company.id])],
                "property_warehouse_id": cls.warehouse_user.id,
            }
        )
        cls.default_company_wh = cls.env["stock.warehouse"].search(
            [("company_id", "=", cls.company.id)], limit=1
        )

    def create_order(self):
        """Helper to open a Sale Order Form with the base fields pre-filled.
        We rely on Form to trigger onchanges automatically when fields change.
        """
        sale = self.env["sale.order"].create(
            {
                "partner_id": self.partner.id,
                "partner_shipping_id": self.partner_shipping.id,
                "user_id": self.user.id,
                "type_id": self.sale_order_type.id,
            }
        )
        return sale

    def test_priority_1_shipping_address(self):
        sale = self.create_order()
        sale.type_id = self.sale_order_type
        self.assertEqual(sale.warehouse_id, self.warehouse_shipping)

    def test_priority_2_partner_when_shipping_missing(self):
        self.partner_shipping.sale_warehouse_id = False
        sale = self.create_order()
        sale.type_id = self.sale_order_type
        self.assertEqual(sale.warehouse_id, self.warehouse_partner)

    def test_priority_3_user_when_shipping_and_partner_missing(self):
        self.partner_shipping.sale_warehouse_id = False
        self.partner.sale_warehouse_id = False
        sale = self.create_order()
        sale.type_id = self.sale_order_type
        self.assertEqual(sale.warehouse_id, self.warehouse_user)

    def test_priority_4_type_when_others_missing(self):
        self.partner_shipping.sale_warehouse_id = False
        self.partner.sale_warehouse_id = False
        self.user.property_warehouse_id = False
        sale = self.create_order()
        sale.type_id = self.sale_order_type
        self.assertEqual(sale.warehouse_id, self.warehouse_type)

    def test_no_override_when_vals_not_found(self):
        self.partner_shipping.sale_warehouse_id = False
        self.partner.sale_warehouse_id = False
        self.user.property_warehouse_id = False
        self.sale_order_type.warehouse_id = False
        sale = self.create_order()
        self.assertEqual(sale.warehouse_id, self.default_company_wh)
