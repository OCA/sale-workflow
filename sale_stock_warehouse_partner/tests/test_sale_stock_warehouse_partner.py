# Copyright 2025 Tecnativa - Eduardo Ezerouali
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl)
from odoo.tests import Form, TransactionCase, tagged


@tagged("post_install", "-at_install")
class TestSaleStockWarehousePartner(TransactionCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.company = cls.env.ref("base.main_company")
        Warehouse = cls.env["stock.warehouse"].with_context(tracking_disable=True)
        cls.warehouse_1 = Warehouse.create(
            {
                "name": "Warehouse 1 - Partner",
                "code": "WH-1",
                "company_id": cls.company.id,
            }
        )
        cls.warehouse_2 = Warehouse.create(
            {
                "name": "Warehouse 2 - Partner Shipping",
                "code": "WH-2",
                "company_id": cls.company.id,
            }
        )
        cls.warehouse_3 = Warehouse.create(
            {
                "name": "Warehouse 3 - User/Comercial",
                "code": "WH-3",
                "company_id": cls.company.id,
            }
        )
        Partner = cls.env["res.partner"]
        cls.partner = Partner.create(
            {"name": "Test Partner", "company_id": cls.company.id}
        )
        cls.partner.sale_warehouse_id = cls.warehouse_1
        cls.partner_shipping = Partner.create(
            {
                "name": "Test Partner - Shipping",
                "type": "delivery",
                "parent_id": cls.partner.id,
                "company_id": cls.company.id,
            }
        )
        cls.partner_shipping.sale_warehouse_id = cls.warehouse_2
        Users = cls.env["res.users"].with_context(tracking_disable=True)
        cls.user = Users.create(
            {
                "name": "Test User",
                "login": "test_user@example.com",
                "company_id": cls.company.id,
                "company_ids": [(6, 0, [cls.company.id])],
            }
        )
        cls.user.property_warehouse_id = cls.warehouse_3
        cls.default_company_wh = cls.env["stock.warehouse"].search(
            [("company_id", "=", cls.company.id)], limit=1
        )

    def _new_order_form(self):
        """Helper to open a Form with company context and trigger onchanges."""
        return Form(self.env["sale.order"].with_context(tracking_disable=True))

    def test_warehouse_priority_and_fallbacks(self):
        with self._new_order_form() as so:
            so.partner_id = self.partner
            so.partner_shipping_id = self.partner_shipping
            so.user_id = self.user
        order = so.save()
        self.assertEqual(
            order.warehouse_id,
            self.warehouse_2,
        )
        self.partner_shipping.sale_warehouse_id = False

        with self._new_order_form() as so:
            so.partner_id = self.partner
            so.partner_shipping_id = self.partner_shipping
            so.user_id = self.user
        order = so.save()
        self.assertEqual(
            order.warehouse_id,
            self.warehouse_1,
        )
        self.partner.sale_warehouse_id = False

        with self._new_order_form() as so:
            so.partner_id = self.partner
            so.partner_shipping_id = self.partner_shipping
            so.user_id = self.user
        order = so.save()
        self.assertEqual(
            order.warehouse_id,
            self.warehouse_3,
        )
        self.user.property_warehouse_id = False
        self.partner_shipping.sale_warehouse_id = False
        self.partner.sale_warehouse_id = False
        with self._new_order_form() as so:
            so.partner_id = self.partner
            so.partner_shipping_id = self.partner_shipping
            so.user_id = self.user
        order = so.save()
        self.assertEqual(
            order.warehouse_id,
            self.default_company_wh,
        )

    def test_onchange_triggers_each_field(self):
        """ "Check that each onchange updates warehouse_id when its field changes."""
        self.partner_shipping.sale_warehouse_id = False
        self.partner.sale_warehouse_id = False
        self.user.property_warehouse_id = False
        with self._new_order_form() as so:
            so.partner_id = self.partner
        order = so.save()

        self.user.property_warehouse_id = self.warehouse_3
        with Form(order) as so_edit:
            so_edit.user_id = self.user
        self.assertEqual(order.warehouse_id, self.warehouse_3)

        self.partner.sale_warehouse_id = self.warehouse_1
        with Form(order) as so_edit:
            so_edit.partner_id = self.partner
        self.assertEqual(order.warehouse_id, self.warehouse_1)

        self.partner_shipping.sale_warehouse_id = self.warehouse_2
        with Form(order) as so_edit:
            so_edit.partner_shipping_id = self.partner_shipping
        self.assertEqual(order.warehouse_id, self.warehouse_2)
