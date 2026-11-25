# Copyright 2019 Akretion Mourad EL HADJ MIMOUNE
# Copyright 2026 OERP Canada <https://www.oerp.ca>
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl.html).

from unittest.mock import patch

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
        # Give fixtures priority over the optional demonstration substates.
        cls.substate_under_nego = cls.base_substate.create(
            {
                "name": "In negotiation",
                "sequence": -20,
                "target_state_value_id": cls.target_draft.id,
            }
        )
        cls.substate_won = cls.base_substate.create(
            {
                "name": "Won",
                "sequence": -10,
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
        self.assertEqual(so_test1.state, "draft")
        self.assertEqual(so_test1.substate_id, self.substate_under_nego)
        # Block substate not corresponding to draft state
        so_test1.action_confirm()
        so_test1.write({"substate_id": self.substate_valid_docs.id})
        self.assertEqual(so_test1.state, "sale")
        self.assertEqual(so_test1.substate_id, self.substate_valid_docs)

        # Test that substate_id is set to false if
        # there is not substate corresponding to state
        so_test1._action_cancel()
        self.assertEqual(so_test1.state, "cancel")
        self.assertFalse(so_test1.substate_id)

    def test_sale_order_explicit_substate(self):
        substate = self.base_substate.create(
            {
                "name": "Quotation reviewed",
                "sequence": 10,
                "target_state_value_id": self.target_draft.id,
            }
        )
        order = self.substate_test_sale.create(
            {
                "partner_id": self.test_partner.id,
                "substate_id": substate.id,
            }
        )
        self.assertEqual(order.substate_id, substate)
        order.write({"note": "Substate must remain unchanged"})
        self.assertEqual(order.substate_id, substate)

    def test_sale_order_substate_batch(self):
        orders = self.substate_test_sale.create(
            [{"partner_id": self.test_partner.id} for _index in range(2)]
        )
        self.assertEqual(orders.mapped("substate_id"), self.substate_under_nego)
        orders.action_confirm()
        self.assertEqual(set(orders.mapped("state")), {"sale"})
        self.assertEqual(orders.mapped("substate_id"), self.substate_won)
        orders.write({"substate_id": self.substate_valid_docs.id})
        self.assertEqual(orders.mapped("substate_id"), self.substate_valid_docs)
        orders._action_cancel()
        self.assertFalse(orders.mapped("substate_id"))
        orders.action_draft()
        self.assertEqual(set(orders.mapped("state")), {"draft"})
        self.assertEqual(orders.mapped("substate_id"), self.substate_under_nego)

    def test_sale_substate_configuration(self):
        substate_type = self.env.ref("sale_substate.base_substate_type_sale")
        self.assertEqual(substate_type.model, "sale.order")
        self.assertEqual(substate_type.target_state_field, "state")
        self.assertEqual(self.target_draft.base_substate_type_id, substate_type)
        self.assertEqual(self.target_sale.base_substate_type_id, substate_type)
        self.assertEqual(self.target_draft.target_state_value, "draft")
        self.assertEqual(self.target_sale.target_state_value, "sale")
        template = self.substate_wait_docs.mail_template_id
        self.assertEqual(template.model_id.model, "sale.order")

    def test_sale_order_substate_mail_template(self):
        order = self.substate_test_sale.create({"partner_id": self.test_partner.id})
        order.action_confirm()
        messages = order.message_ids
        with patch.object(type(self.env["ir.mail_server"]), "send_email") as send_email:
            order.write({"substate_id": self.substate_wait_docs.id})
            self.env.flush_all()
            send_email.assert_not_called()
        new_messages = order.message_ids - messages
        self.assertEqual(order.substate_id, self.substate_wait_docs)
        self.assertTrue(
            any(
                "In order to validate your order we need the legal documentation."
                in message.body
                for message in new_messages
            )
        )
