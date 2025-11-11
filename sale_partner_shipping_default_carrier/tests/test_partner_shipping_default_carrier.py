# Copyright 2025 Quartile (https://www.quartile.co)
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl.html).


from odoo import Command
from odoo.tests import TransactionCase


class TestSalePartnerShippingDefaultCarrier(TransactionCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.partner = cls.env["res.partner"].create({"name": "Test Partner"})
        cls.product = cls.env["product.product"].create({"name": "Test Product"})
        cls.carrier = cls.env["delivery.carrier"].create(
            {"name": "Test Carrier", "product_id": cls.product.id}
        )

    def create_sale_order(self):
        return self.env["sale.order"].create(
            {
                "partner_id": self.partner.id,
                "order_line": [
                    Command.create(
                        {
                            "product_id": self.product.id,
                            "product_uom_qty": 1,
                        }
                    )
                ],
            }
        )

    def test_sale_order_carrier(self):
        sale_order = self.create_sale_order()
        self.assertNotEqual(sale_order.carrier_id, self.carrier)
        self.partner.property_delivery_carrier_id = self.carrier.id
        sale_order = self.create_sale_order()
        self.assertEqual(sale_order.carrier_id, self.carrier)
