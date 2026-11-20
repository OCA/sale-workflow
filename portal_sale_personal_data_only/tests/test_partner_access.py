# Copyright 2021 Tecnativa - Víctor Martínez
# Copyright 2022 Moduon
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl)

from odoo.tests import Form, tagged

from odoo.addons.account.tests.common import AccountTestInvoicingCommon


@tagged("post_install", "-at_install")
class TestPartnerAccess(AccountTestInvoicingCommon):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.group_portal = cls.env.ref("base.group_portal")
        cls.user_a = cls._create_user(cls, "A")
        cls.user_b = cls._create_user(cls, "B")
        cls.user_c = cls._create_user(cls, "C")
        cls.partner_a = cls._create_partner(cls, cls.user_a)
        cls.partner_b = cls._create_partner(cls, cls.user_b)
        cls.partner_c = cls._create_partner(cls, cls.user_c)
        cls.product = cls.env["product.product"].create(
            {
                "name": "Test product",
                "type": "service",
                "lst_price": 10,
                "invoice_policy": "order",
            }
        )
        cls.order_a = cls._create_sale_order(cls, cls.partner_a)
        cls.order_b = cls._create_sale_order(cls, cls.partner_b)
        cls.order_c = cls._create_sale_order(cls, cls.partner_c)

    def _create_user(self, letter):
        return self.env["res.users"].create(
            {
                "name": f"User {letter}",
                "login": f"user_{letter}",
                "group_ids": [(6, 0, [self.group_portal.id])],
            }
        )

    def _create_partner(self, user):
        return self.env["res.partner"].create(
            {
                "name": user.name,
                "user_ids": [(6, 0, [user.id])],
            }
        )

    def _create_sale_order(self, partner):
        sale_form = Form(self.env["sale.order"].sudo())
        sale_form.partner_id = partner
        with sale_form.order_line.new() as line_form:
            line_form.product_id = self.product
        sale = sale_form.save()
        sale.action_confirm()
        sale._create_invoices()
        return sale

    def test_access_sale_order(self):
        # Access is granted as the customer, with no need to be a follower
        self.assertNotIn(self.partner_a, self.order_a.message_partner_ids)
        orders_a = self.env["sale.order"].with_user(self.user_a).search([])
        self.assertIn(self.order_a, orders_a)
        self.assertNotIn(self.order_b, orders_a)
        self.assertNotIn(self.order_c, orders_a)
        orders_b = self.env["sale.order"].with_user(self.user_b).search([])
        self.assertNotIn(self.order_a, orders_b)
        self.assertIn(self.order_b, orders_b)
        self.assertNotIn(self.order_c, orders_b)
        orders_c = self.env["sale.order"].with_user(self.user_c).search([])
        self.assertNotIn(self.order_a, orders_c)
        self.assertNotIn(self.order_b, orders_c)
        self.assertIn(self.order_c, orders_c)

    def test_access_sale_order_followers(self):
        # Being a follower grants access in addition to being the direct customer
        orders_b = self.env["sale.order"].with_user(self.user_b).search([])
        self.assertNotIn(self.order_a, orders_b)
        self.order_a.message_subscribe(partner_ids=self.partner_b.ids)
        orders_b = self.env["sale.order"].with_user(self.user_b).search([])
        self.assertIn(self.order_a, orders_b)

    def test_access_sale_order_same_commercial_partner(self):
        # Contacts of the same company only see their own sale orders, unlike
        # the core rule, which grants access to the whole commercial partner
        company = self.env["res.partner"].create(
            {"name": "Company", "is_company": True}
        )
        (self.partner_a | self.partner_b).parent_id = company
        order_company = self._create_sale_order(company)
        orders_a = self.env["sale.order"].with_user(self.user_a).search([])
        self.assertIn(self.order_a, orders_a)
        self.assertNotIn(self.order_b, orders_a)
        self.assertNotIn(order_company, orders_a)

    def test_access_sale_order_child_contact(self):
        delivery_address = self.env["res.partner"].create(
            {
                "name": "Delivery address A",
                "type": "delivery",
                "parent_id": self.partner_a.id,
            }
        )
        order = self._create_sale_order(delivery_address)
        orders_a = self.env["sale.order"].with_user(self.user_a).search([])
        self.assertIn(order, orders_a)
        orders_b = self.env["sale.order"].with_user(self.user_b).search([])
        self.assertNotIn(order, orders_b)

    def test_access_invoice(self):
        invoice_a = self.order_a.invoice_ids
        invoice_b = self.order_b.invoice_ids
        # Draft invoices are not accessible
        invoices_a = self.env["account.move"].with_user(self.user_a).search([])
        self.assertNotIn(invoice_a, invoices_a)
        (invoice_a | invoice_b).action_post()
        invoices_a = self.env["account.move"].with_user(self.user_a).search([])
        self.assertIn(invoice_a, invoices_a)
        self.assertNotIn(invoice_b, invoices_a)
        lines_a = self.env["account.move.line"].with_user(self.user_a).search([])
        self.assertTrue(invoice_a.line_ids <= lines_a)
        self.assertFalse(invoice_b.line_ids & lines_a)

    def test_access_invoice_sale_order_followers(self):
        # Following the sale order grants access to its posted invoices
        invoice_a = self.order_a.invoice_ids
        invoice_a.action_post()
        self.order_a.message_subscribe(partner_ids=self.partner_b.ids)
        self.assertNotIn(self.partner_b, invoice_a.message_partner_ids)
        invoices_b = self.env["account.move"].with_user(self.user_b).search([])
        self.assertIn(invoice_a, invoices_b)
        lines_b = self.env["account.move.line"].with_user(self.user_b).search([])
        self.assertTrue(invoice_a.invoice_line_ids <= lines_b)
