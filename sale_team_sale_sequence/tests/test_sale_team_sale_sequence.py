# Copyright 2026 ForgeFlow S.L. (https://www.forgeflow.com)
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).

from odoo.tests import TransactionCase


class TestSaleTeamSaleSequence(TransactionCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.env = cls.env(context=dict(cls.env.context, tracking_disable=True))
        cls.partner = cls.env["res.partner"].create({"name": "Test Partner"})
        cls.sequence = cls.env["ir.sequence"].create(
            {
                "name": "Test Team Sale Sequence",
                "code": "test.sale.team.sale.sequence",
                "prefix": "TEAM/",
                "padding": 4,
            }
        )
        cls.team = cls.env["crm.team"].create(
            {
                "name": "Test Sales Team",
                "sequence_id": cls.sequence.id,
            }
        )

    def test_sale_order_uses_team_sequence(self):
        order = self.env["sale.order"].create(
            {"partner_id": self.partner.id, "team_id": self.team.id}
        )
        self.assertTrue(order.name.startswith("TEAM/"))
        self.assertEqual(order.sequence_id, self.sequence)

    def test_sale_order_without_team_sequence_uses_default(self):
        team_no_seq = self.env["crm.team"].create({"name": "Team No Sequence"})
        order = self.env["sale.order"].create(
            {"partner_id": self.partner.id, "team_id": team_no_seq.id}
        )
        self.assertFalse(order.name.startswith("TEAM/"))
        self.assertFalse(order.sequence_id)

    def test_sequence_mismatch_detected(self):
        order = self.env["sale.order"].create(
            {"partner_id": self.partner.id, "team_id": self.team.id}
        )
        self.assertFalse(order.sequence_mismatch)
        other_seq = self.env["ir.sequence"].create(
            {"name": "Other Sequence", "prefix": "OTHER/", "padding": 4}
        )
        order.sequence_id = other_seq
        self.assertTrue(order.sequence_mismatch)

    def test_renumber_from_team_sequence(self):
        order = self.env["sale.order"].create(
            {"partner_id": self.partner.id, "team_id": self.team.id}
        )
        other_seq = self.env["ir.sequence"].create(
            {"name": "Other Sequence 2", "prefix": "OTHER2/", "padding": 4}
        )
        order.sequence_id = other_seq
        self.assertTrue(order.sequence_mismatch)
        order.action_renumber_from_team_sequence()
        self.assertTrue(order.name.startswith("TEAM/"))
        self.assertEqual(order.sequence_id, self.sequence)
        self.assertFalse(order.sequence_mismatch)
