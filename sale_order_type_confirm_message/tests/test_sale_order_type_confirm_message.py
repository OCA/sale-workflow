# Copyright 2024 Alberto Martínez <alberto.martinez@sygel.es>
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).

from odoo.tests.common import Form, TransactionCase


class TestSaleOrderTypeConfirmMessage(TransactionCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.partner = cls.env["res.partner"].create({"name": "Test Partner"})
        cls.order_type = cls.env["sale.order.type"].create(
            {
                "name": "Test Category",
                "confirmation_message": "It works!!",
                "has_confirmation_message": True,
            }
        )
        cls.sale = cls.env["sale.order"].create(
            {"partner_id": cls.partner.id, "type_id": cls.order_type.id}
        )

    def test_sale_order_type_confirm_message(self):
        res = self.sale.action_confirm()
        self.assertEqual(type(res), dict)
        self.assertEqual(res["res_model"], "sale.order.type.confirm.wizard")

    def test_sale_order_type_no_confirm_message(self):
        self.order_type.write({"has_confirmation_message": False})
        res = self.sale.action_confirm()
        self.assertNotEqual(type(res), dict)

    def test_sale_order_confirm(self):
        wizard_form = Form(
            self.env["sale.order.type.confirm.wizard"].with_context(
                **{"active_id": self.sale.id}
            )
        )
        wizard_rec = wizard_form.save()
        wizard_rec.action_confirm()
        self.assertEqual(self.sale.state, "sale")
