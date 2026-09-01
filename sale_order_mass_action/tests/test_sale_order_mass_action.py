# Copyright 2021 ACSONE SA/NV
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).
from odoo.tests import Form

from odoo.addons.base.tests.common import BaseCommon


class TestSaleOrderMassAction(BaseCommon):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.sale_order_obj = cls.env["sale.order"]
        cls.product = cls.env["product.product"].create(
            {
                "name": "Virtual Interior Design",
                "categ_id": cls.env.ref("product.product_category_services").id,
                "standard_price": 20.5,
                "list_price": 30.75,
                "type": "service",
                "uom_id": cls.env.ref("uom.product_uom_hour").id,
            }
        )
        cls.wizard_obj = cls.env["sale.order.mass.action.wizard"]
        vals = {
            "name": "sale Order Mass 1",
            "partner_id": cls.partner.id,
        }
        cls.sale = cls.sale_order_obj.create(vals)

        with Form(cls.sale) as sale_form:
            with sale_form.order_line.new() as line_form:
                line_form.product_id = cls.product

    def test_sale_confirm(self):
        # Launch the wizard on Sale Order
        # Set Confirm
        # Check if the sale order is confirmed
        self.wizard = self.wizard_obj.with_context(
            active_model="sale.order", active_ids=[self.sale.id]
        ).create({})
        with Form(self.wizard) as wizard_form:
            wizard_form.action = "confirm"
        self.wizard.apply_button()
        self.assertEqual("sale", self.sale.state)

    def test_sale_confirm_cancelled(self):
        # Cancel the Sale Order
        # Launch the wizard on Sale Order
        # Choose confirm action
        # Check if the sale order is still cancelled
        self.sale.write({"state": "cancel"})
        self.wizard = self.wizard_obj.with_context(
            active_model="sale.order", active_ids=[self.sale.id]
        ).create({})
        with Form(self.wizard) as wizard_form:
            wizard_form.action = "confirm"
        self.wizard.apply_button()
        self.assertEqual("cancel", self.sale.state)

    def test_sale_quotation_sent(self):
        # Launch the wizard on Sale Order
        # Choose quotation sent action
        # Check if the sale order is confirmed
        self.wizard = self.wizard_obj.with_context(
            active_model="sale.order", active_ids=[self.sale.id]
        ).create({})
        with Form(self.wizard) as wizard_form:
            wizard_form.action = "quotation_sent"
        self.wizard.apply_button()
        self.assertEqual("sent", self.sale.state)

    def test_sale_lock(self):
        # with an unlocked sale
        # Launch the wizard on Sale Order
        # Choose lock action
        # Check if the sale order is locked
        self.assertFalse(self.sale.locked)
        self.wizard = self.wizard_obj.with_context(
            active_model="sale.order", active_ids=[self.sale.id]
        ).create({})
        with Form(self.wizard) as wizard_form:
            wizard_form.action = "lock"
        self.wizard.apply_button()
        self.assertTrue(self.sale.locked)

    def test_sale_unlock(self):
        # with an locked sale
        # Launch the wizard on Sale Order
        # Choose unlock action
        # Check if the sale order is locked
        self.sale.locked = True
        self.assertTrue(self.sale.locked)
        self.wizard = self.wizard_obj.with_context(
            active_model="sale.order", active_ids=[self.sale.id]
        ).create({})
        with Form(self.wizard) as wizard_form:
            wizard_form.action = "unlock"
        self.wizard.apply_button()
        self.assertFalse(self.sale.locked)

    def test_sale_cancel(self):
        # Launch the wizard on Sale Order
        # Choose cancel action
        # Check if the sale order is confirmed
        self.wizard = self.wizard_obj.with_context(
            active_model="sale.order", active_ids=[self.sale.id]
        ).create({})
        with Form(self.wizard) as wizard_form:
            wizard_form.action = "cancel"
        self.wizard.apply_button()
        self.assertEqual("cancel", self.sale.state)

    def test_sale_draft(self):
        # Launch the wizard on Sale Order
        # Choose draft action
        # Check if the sale order is confirmed
        self.sale.action_quotation_sent()
        self.wizard = self.wizard_obj.with_context(
            active_model="sale.order", active_ids=[self.sale.id]
        ).create({})
        with Form(self.wizard) as wizard_form:
            wizard_form.action = "draft"
        self.wizard.apply_button()
        self.assertEqual("draft", self.sale.state)
