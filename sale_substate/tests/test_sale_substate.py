# Copyright 2019 Akretion Mourad EL HADJ MIMOUNE
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl.html).

from odoo.exceptions import ValidationError
from odoo.tests.common import TransactionCase


class TestBaseSubstate(TransactionCase):
    def setUp(self):
        super(TestBaseSubstate, self).setUp()
        self.substate_test_sale = self.env["sale.order"]
        self.substate_test_sale_line = self.env["sale.order.line"]

        self.substate_under_nego = self.env.ref(
            "sale_substate.base_substate_under_nego"
        )
        self.substate_won = self.env.ref("sale_substate.base_substate_won")
        self.substate_wait_docs = self.env.ref("sale_substate.base_substate_wait_docs")
        self.substate_valid_docs = self.env.ref(
            "sale_substate.base_substate_valid_docs"
        )
        self.substate_in_delivery = self.env.ref(
            "sale_substate.base_substate_in_delivery"
        )
        self.product_1 = self.env["product.product"].create(
            {
                "name": "Test Product 1",
                "type": "service",
            }
        )

    def test_sale_order_substate(self):
        partner = self.env.ref("base.res_partner_1")
        so_test1 = self.substate_test_sale.create(
            {
                "name": "Test base substate to basic sale",
                "partner_id": partner.id,
                "order_line": [
                    (
                        0,
                        0,
                        {
                            "product_id": self.product_1.id,
                            "product_uom_qty": 2,
                            "product_uom": self.product_1.uom_id.id,
                            "name": "line test",
                            "price_unit": 120.0,
                        },
                    )
                ],
            }
        )
        self.assertTrue(so_test1.state == "draft")
        self.assertTrue(so_test1.substate_id == self.substate_under_nego)

        # Block substate not corresponding to draft state
        with self.assertRaises(ValidationError):
            so_test1.substate_id = self.substate_valid_docs
        # Test that validation of sale order change substate_id
        so_test1.action_confirm()
        self.assertTrue(so_test1.state == "sale")
        self.assertTrue(so_test1.substate_id == self.substate_valid_docs)

        # Test that substate_id is set to false if
        # there is not substate corresponding to state
        so_test1.action_cancel()
        self.assertTrue(so_test1.state == "cancel")
        self.assertTrue(not so_test1.substate_id)
