# Copyright 2023 ACSONE SA/NV (<http://acsone.eu>)
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo.tests.common import TransactionCase


class TestSaleOrder(TransactionCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.env = cls.env(context=dict(cls.env.context, tracking_disable=True))
        cls.partner_1 = cls.env["res.partner"].create(
            {"name": "partner_1", "company_id": cls.env.company.id}
        )
        cls.partner_2 = cls.env["res.partner"].create(
            {"name": "partner_2", "company_id": cls.env.company.id}
        )
        cls.partner_1.write(
            {"sale_order_note": "Sale Default Terms and Conditions Partner"}
        )

    def test_onchange_partner_id(self):

        self.product = self.env["product.product"].create(
            {"name": "test_product", "type": "service"}
        )
        order = self.env["sale.order"].create(
            {
                "partner_id": self.partner_2.id,
                "order_line": [
                    (
                        0,
                        0,
                        {
                            "name": self.product.name,
                            "product_id": self.product.id,
                            "product_uom_qty": 1,
                            "product_uom": self.product.uom_id.id,
                            "price_unit": 1000.00,
                        },
                    )
                ],
                "pricelist_id": self.env.ref("product.list0").id,
            }
        )

        self.assertFalse(order.note)
        order.write({"partner_id": self.partner_1.id})
        self.assertNotIn("Company Terms", order.note)
