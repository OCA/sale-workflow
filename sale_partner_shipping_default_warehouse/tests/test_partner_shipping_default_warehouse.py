# Copyright 2025 Quartile (https://www.quartile.co)
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl.html).


from odoo.tests import TransactionCase


class TestSalePartnerShippingDefaultWarehouse(TransactionCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.partner = cls.env["res.partner"].create({"name": "Test Partner"})
        cls.partner_shipping = cls.env["res.partner"].create(
            {"name": "Test Shipping Partner"}
        )
        cls.warehouse = cls.env["stock.warehouse"].create(
            {"name": "Test Warehouse", "code": "TW"}
        )
        cls.product = cls.env["product.product"].create({"name": "Test Product"})

    def create_sale_order(self):
        return self.env["sale.order"].create(
            {
                "partner_id": self.partner.id,
                "partner_shipping_id": self.partner_shipping.id,
            }
        )

    def test_sale_order_warehouse(self):
        sale_order = self.create_sale_order()
        self.assertNotEqual(sale_order.warehouse_id, self.warehouse)
        self.partner_shipping.default_sale_warehouse_id = self.warehouse.id
        sale_order = self.create_sale_order()
        self.assertEqual(sale_order.warehouse_id, self.warehouse)
