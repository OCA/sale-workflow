# Copyright (C) 2018 - Today: GRAP (http://www.grap.coop)
# @author: Sylvain LE GAL (https://twitter.com/legalsylvain)
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

from odoo.tests.common import TransactionCase


class TestSaleOrderRecurrence(TransactionCase):
    def setUp(self):
        super(TestSaleOrderRecurrence, self).setUp()
        self.wizard_obj = self.env["sale.order.recurrence.wizard"]
        self.order_obj = self.env["sale.order"]
        self.order = self.env.ref("sale.sale_order_6")

    # Test Section
    def test_01_duplicate_quotation(self):
        quotation_qty = len(self.order_obj.search([]))
        wizard = self.wizard_obj.create(
            {
                "order_id": self.order.id,
                "partner_id": self.order.partner_id.id,
                "begin_date": "2024-01-01",
                "include_current_date": False,
                "recurrence_type": "week",
                "recurrence_duration": 3,
            }
        )
        # test open button and weekly recurrence
        wizard.onchange_recurrence_settings()
        wizard.duplicate_open_button()
        new_quotation_qty = len(self.order_obj.search([]))
        self.assertEqual(
            quotation_qty + 3,
            new_quotation_qty,
            "Duplication wizard should create new sale orders",
        )

        # test other button and monthly recurrence
        wizard = self.wizard_obj.create(
            {
                "order_id": self.order.id,
                "partner_id": self.order.partner_id.id,
                "begin_date": "2025-01-01",
                "include_current_date": True,
                "recurrence_type": "month",
                "recurrence_duration": 5,
            }
        )
        wizard.onchange_recurrence_settings()
        wizard.duplicate_button()
        new_quotation_qty = len(self.order_obj.search([]))
        self.assertEqual(
            quotation_qty + 3 + 5,
            new_quotation_qty,
            "Duplication wizard should create new sale orders",
        )

    def test_02_wzd_default_get(self):
        wzd_obj = self.wizard_obj.with_context(
            active_id=self.order.id,
        )
        result = wzd_obj.default_get(
            fields_list=[],
        )
        self.assertEqual(
            result["order_id"],
            self.order.id,
        )
        self.assertEqual(
            result["partner_id"],
            self.order.partner_id.id,
        )
