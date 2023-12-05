# Copyright 2023 Moduon Team S.L.
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl-3.0)


from odoo.tests.common import TransactionCase


class TestPartnerPickingNote(TransactionCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.partner = cls.env["res.partner"].create(
            {
                "name": "Test Partner",
                "picking_note": "<p>Test note</p>",
                "picking_customer_note": "Test customer note",
            }
        )

    def test_partner_picking_note(self):
        sale = self.env["sale.order"].create({"partner_id": self.partner.id})
        self.assertRecordValues(
            sale,
            [
                {
                    "picking_note": "<p>Test note</p>",
                    "picking_customer_note": "Test customer note",
                }
            ],
        )
