from odoo.exceptions import ValidationError
from odoo.tests import Form

from odoo.addons.base.tests.common import BaseCommon


class TestSaleOrder(BaseCommon):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.partner1 = cls.env["res.partner"].create({"name": "Test Partner 1"})
        cls.child_1 = cls.env["res.partner"].create(
            {"name": "Child 1", "parent_id": cls.partner1.id, "type": "delivery"}
        )
        cls.child_2 = cls.env["res.partner"].create(
            {"name": "Child 2", "parent_id": cls.partner1.id}
        )

        cls.partner2 = cls.env["res.partner"].create({"name": "Test Partner 2"})
        cls.partner3 = cls.env["res.partner"].create({"name": "Test Partner 3"})

        cls.env.user.groups_id += cls.env.ref("account.group_delivery_invoice_address")
        cls.env.company.sale_partner_address_restriction = True

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

    def test_sale_order_partner_unallowed(self):
        order_form = Form(self.env["sale.order"])
        order_form.partner_id = self.partner1
        sale_order = order_form.save()
        with self.assertRaises(ValidationError):
            with Form(sale_order) as sale_order:
                sale_order.partner_shipping_id = self.partner3

    def test_sale_order_partner_allowed(self):
        self.env.company.sale_partner_address_restriction = False
        order_form = Form(self.env["sale.order"])
        order_form.partner_id = self.partner1
        sale_order = order_form.save()
        with Form(sale_order) as sale_order:
            sale_order.partner_shipping_id = self.partner3

    def test_sale_order_address_constraint(self):
        with self.assertRaises(ValidationError):
            self.env["sale.order"].create(
                {
                    "partner_id": self.partner1.id,
                    "partner_invoice_id": self.partner2.id,
                    "partner_shipping_id": self.child_2.id,
                }
            )

    def test_sale_order_address_no_constraint(self):
        self.env.company.sale_partner_address_restriction = False
        self.env["sale.order"].create(
            {
                "partner_id": self.partner1.id,
                "partner_invoice_id": self.partner2.id,
                "partner_shipping_id": self.child_2.id,
            }
        )

    def test_dropship_delivery_address(self):
        self.assertIn(self.partner1.name, self.child_1.display_name)
        self.child_1.is_dropship_address = True
        self.child_1._compute_display_name()
        self.assertNotIn(self.partner1.name, self.child_1.display_name)
