from odoo.exceptions import ValidationError
from odoo.tests import Form
from odoo.tests.common import TransactionCase


class TestSaleOrder(TransactionCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.partner1 = cls.env["res.partner"].create({"name": "Test Partner 1"})
        cls.child_1 = cls.env["res.partner"].create(
            {"name": "Child 1", "parent_id": cls.partner1.id}
        )
        cls.child_2 = cls.env["res.partner"].create(
            {"name": "Child 2", "parent_id": cls.partner1.id}
        )

        cls.partner2 = cls.env["res.partner"].create({"name": "Test Partner 2"})
        cls.partner3 = cls.env["res.partner"].create({"name": "Test Partner 3"})

    def test_sale_order_address_domain(self):
        order_form = Form(self.env["sale.order"])
        order_form.partner_id = self.partner1
        sale_order = order_form.save()

        expected_domain = [
            ("commercial_partner_id", "=", sale_order.partner_id.id),
            "|",
            ("company_id", "=", False),
            ("company_id", "=", sale_order.company_id.id),
        ]

        partners = self.env["res.partner"].search(expected_domain)
        self.assertEqual(len(partners), 3)

        with Form(sale_order) as sale_order:
            sale_order.partner_id = self.partner2
            expected_domain = [
                ("commercial_partner_id", "=", sale_order.partner_id.id),
                "|",
                ("company_id", "=", False),
                ("company_id", "=", sale_order.company_id.id),
            ]
            partners = self.env["res.partner"].search(expected_domain)
            self.assertEqual(len(partners), 1)

    def test_sale_order_address_constraint(self):
        with self.assertRaises(ValidationError):
            self.env["sale.order"].create(
                {
                    "partner_id": self.partner1.id,
                    "partner_invoice_id": self.partner2.id,
                    "partner_shipping_id": self.child_2.id,
                }
            )
