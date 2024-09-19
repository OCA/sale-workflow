# Copyright 2021 Open Source Integrators
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).
from odoo.exceptions import UserError
from odoo.tests import tagged
from odoo.tests.common import TransactionCase


@tagged("post_install", "-at_install")
class TestSaleProductApproval(TransactionCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.customer = cls.env.ref("base.res_partner_12")
        cls.product_state_sale = cls.env.ref("product_state.product_state_sellable")
        cls.product_state_end = cls.env.ref("product_state.product_state_end")
        cls.product_id = cls.env["product.product"].create(
            {"name": "Test Product", "type": "product"}
        )
        cls.sale_id = cls.env["sale.order"].create(
            {
                "partner_id": cls.customer.id,
                "order_line": [
                    (
                        0,
                        0,
                        {
                            "product_id": cls.product_id.id,
                            "product_uom_qty": 2.0,
                            "price_unit": 10.0,
                        },
                    )
                ],
            }
        )

    def test_write_product_state(self):
        self.product_id.write({"product_state_id": self.product_state_sale.id})
        self.product_state_end.write({"approved_sale": False})
        self.product_id.write({"product_state_id": self.product_state_end.id})
        with self.assertRaises(UserError):
            self.sale_id.action_confirm()
        self.product_id.write({"product_state_id": self.product_state_sale.id})
