# Copyright 2021 Tecnativa - Víctor Martínez
# Copyright 2022 Moduon
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl)

from odoo.tests.common import Form, tagged

from odoo.addons.account.tests.common import TestAccountReconciliationCommon


@tagged("post_install", "-at_install")
class TestPartnerAccess(TestAccountReconciliationCommon):
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
                "name": "User %s" % letter,
                "login": "user_%s" % letter,
                "groups_id": [(6, 0, [self.group_portal.id])],
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
        sale_form = Form(self.env["sale.order"])
        sale_form.partner_id = partner
        with sale_form.order_line.new() as line_form:
            line_form.product_id = self.product
        sale = sale_form.save()
        sale.action_confirm()
        sale._create_invoices()
        return sale

    def test_access_sale_order(self):
        orders_a = self.env["sale.order"].with_user(self.user_a).search([])
        self.assertTrue(self.order_a in orders_a)
        self.assertTrue(self.order_b not in orders_a)
        self.assertTrue(self.order_c not in orders_a)
        orders_b = self.env["sale.order"].with_user(self.user_b).search([])
        self.assertTrue(self.order_a not in orders_b)
        self.assertTrue(self.order_b in orders_b)
        self.assertTrue(self.order_c not in orders_b)
        orders_c = self.env["sale.order"].with_user(self.user_c).search([])
        self.assertTrue(self.order_a not in orders_c)
        self.assertTrue(self.order_b not in orders_c)
        self.assertTrue(self.order_c in orders_c)

    def test_access_sale_order_followers(self):
        self.order_a.message_subscribe(partner_ids=self.partner_b.ids)
        orders_b = self.env["sale.order"].with_user(self.user_b).search([])
        self.assertTrue(self.order_a in orders_b)
