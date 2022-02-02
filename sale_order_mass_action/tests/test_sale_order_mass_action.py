# Copyright 2021 ACSONE SA/NV
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).
from odoo.tests import Form
from odoo.tests.common import SavepointCase


class TestSaleOrderMassAction(SavepointCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.env = cls.env(context=dict(cls.env.context, tracking_disable=True))
        cls.sale_order_obj = cls.env["sale.order"]
        cls.partner = cls.env.ref("base.res_partner_2")
        cls.product = cls.env.ref("product.product_product_2")
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
            wizard_form.confirm = True
        self.wizard.apply_button()
        self.assertEqual("sale", self.sale.state)

    def test_sale_confirm_cancelled(self):
        # Cancel the Sale Order
        # Launch the wizard on Sale Order
        # Set Confirm
        # Check if the sale order is still cancelled
        self.sale.write({"state": "cancel"})
        self.wizard = self.wizard_obj.with_context(
            active_model="sale.order", active_ids=[self.sale.id]
        ).create({})
        with Form(self.wizard) as wizard_form:
            wizard_form.confirm = True
        self.wizard.apply_button()
        self.assertEqual("cancel", self.sale.state)
