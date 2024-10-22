# Copyright 2021 Open Source Integrators
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).


from odoo.exceptions import UserError
from odoo.tests.common import TransactionCase


class TestSaleOrderLineDates(TransactionCase):
    def setUp(self):
        super(TestSaleOrderLineDates, self).setUp()
        self.customer = self.env.ref("base.res_partner_12")
        self.product_id = self.test_create_product_template()
        self.sale_id = self.test_sale_order()
        self.product_state_sale = self.env.ref("product_state.product_state_sellable")
        self.product_state_end = self.env.ref("product_state.product_state_end")

    def test_create_product_template(self):
        product = self.env["product.product"].create(
            {"name": "Test Product", "type": "product"}
        )
        return product

    def test_sale_order(self):
        sale = self.env["sale.order"].create(
            {
                "partner_id": self.customer.id,
                "order_line": [
                    (
                        0,
                        0,
                        {
                            "product_id": self.product_id.id,
                            "product_uom_qty": 2.0,
                            "price_unit": 10.0,
                        },
                    )
                ],
            }
        )
        return sale

    def test_write_product_state(self):
        self.product_id.write({"product_state_id": self.product_state_sale.id})
        self.product_state_end.write({"approved_sale": False})
        self.product_id.write({"product_state_id": self.product_state_end.id})
        with self.assertRaises(UserError):
            self.sale_id.action_confirm()
        self.product_id.write({"product_state_id": self.product_state_sale.id})
