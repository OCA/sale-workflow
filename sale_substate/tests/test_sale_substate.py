# Copyright 2019 Akretion Mourad EL HADJ MIMOUNE
# Copyright 2026 OERP Canada <https://www.oerp.ca>
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl.html).

from odoo.tests import tagged
from odoo.tests.common import TransactionCase


@tagged("-at_install", "post_install")
class TestBaseSubstate(TransactionCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.substate_test_sale = cls.env["sale.order"]
        cls.substate_test_sale_line = cls.env["sale.order.line"]
        cls.base_substate = cls.env["base.substate"]
        cls.target_draft = cls.env.ref("sale_substate.target_state_value_draft")
        cls.target_sale = cls.env.ref("sale_substate.target_state_value_sale")
        cls.substate_under_nego = cls.base_substate.create(
            {
                "name": "In negotiation",
                "sequence": 1,
                "target_state_value_id": cls.target_draft.id,
            }
        )
        cls.substate_won = cls.base_substate.create(
            {
                "name": "Won",
                "sequence": 2,
                "target_state_value_id": cls.target_sale.id,
            }
        )
        cls.substate_wait_docs = cls.base_substate.create(
            {
                "name": "Waiting for legal documents",
                "sequence": 4,
                "target_state_value_id": cls.target_sale.id,
                "mail_template_id": cls.env.ref(
                    "sale_substate.mail_template_data_sale_substate_wait_docs"
                ).id,
            }
        )
        cls.substate_valid_docs = cls.base_substate.create(
            {
                "name": "To validate legal documents",
                "sequence": 5,
                "target_state_value_id": cls.target_sale.id,
            }
        )
        cls.substate_in_delivery = cls.base_substate.create(
            {
                "name": "In delivering",
                "sequence": 6,
                "target_state_value_id": cls.target_sale.id,
            }
        )
        cls.product_1 = cls.env["product.product"].create(
            {
                "name": "Test Product 1",
                "type": "service",
            }
        )
        cls.test_partner = cls.env["res.partner"].create(
            {
                "name": "Test Partner",
                "email": "test@example.com",
            }
        )

    def test_sale_order_substate(self):
        so_test1 = self.substate_test_sale.create(
            {
                "name": "Test base substate to basic sale",
                "partner_id": self.test_partner.id,
                "order_line": [
                    (
                        0,
                        0,
                        {
                            "product_id": self.product_1.id,
                            "product_uom_qty": 2,
                            "product_uom_id": self.product_1.uom_id.id,
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
        so_test1.action_confirm()
        so_test1.write({"substate_id": self.substate_valid_docs.id})
        self.assertTrue(so_test1.state == "sale")
        self.assertEqual(so_test1.substate_id, self.substate_valid_docs)

        # Test that substate_id is set to false if
        # there is not substate corresponding to state
        so_test1._action_cancel()
        self.assertTrue(so_test1.state == "cancel")
        self.assertTrue(not so_test1.substate_id)
