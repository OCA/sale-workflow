# Copyright 2026 ForgeFlow S.L. (https://www.forgeflow.com)
# License LGPL-3.0 or later (https://www.gnu.org/licenses/lgpl).

from odoo.exceptions import AccessError
from odoo.tests.common import TransactionCase

from odoo.addons.sale_partner_sale_contact.controllers.portal import CustomerPortal


class TestPortalSaleContact(TransactionCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()

        cls.partner_company = cls.env["res.partner"].create(
            {
                "name": "Test Company",
                "is_company": True,
            }
        )
        cls.contact_person = cls.env["res.partner"].create(
            {
                "name": "John Doe",
                "is_company": False,
                "parent_id": cls.partner_company.id,
                "type": "contact",
                "email": "john.doe@example.com",
            }
        )
        cls.other_contact = cls.env["res.partner"].create(
            {
                "name": "Jane Smith",
                "is_company": False,
                "parent_id": cls.partner_company.id,
                "type": "contact",
                "email": "jane.smith@example.com",
            }
        )
        cls.portal_user = (
            cls.env["res.users"]
            .with_context(no_reset_password=True)
            .create(
                {
                    "name": "John Doe",
                    "login": "john.doe@example.com",
                    "partner_id": cls.contact_person.id,
                    "group_ids": [(6, 0, [cls.env.ref("base.group_portal").id])],
                }
            )
        )
        cls.product = cls.env["product.product"].create(
            {
                "name": "Test Product",
                "list_price": 100.0,
                "type": "consu",
            }
        )
        cls.order = cls.env["sale.order"].create(
            {
                "partner_id": cls.partner_company.id,
                "sale_contact_partner_id": cls.contact_person.id,
                "order_line": [
                    (
                        0,
                        0,
                        {
                            "product_id": cls.product.id,
                            "product_uom_qty": 1.0,
                            "price_unit": 100.0,
                        },
                    )
                ],
            }
        )
        cls.order.action_confirm()
        # Deactivate the standard portal rule (partner_id based) to isolate
        # the access path granted by the sale contact rule.
        cls.env.ref("sale.sale_order_rule_portal").active = False
        cls.env.ref("sale.sale_order_line_rule_portal").active = False

    def test_01_sale_contact_can_read_order(self):
        """The named sale contact can read the order and its lines even
        when the standard partner-based portal rule does not apply."""
        order = self.order.with_user(self.portal_user)
        order.invalidate_recordset()
        self.assertEqual(order.name, self.order.name)
        self.assertEqual(len(order.order_line), 1)

    def test_02_sale_contact_cannot_write_order(self):
        """The sale contact rule is read-only."""
        order = self.order.with_user(self.portal_user)
        with self.assertRaises(AccessError):
            order.client_order_ref = "I should not be able to write this"

    def test_03_other_contact_cannot_read_order(self):
        """A portal user that is not the sale contact gets no access
        through the sale contact rule."""
        other_user = (
            self.env["res.users"]
            .with_context(no_reset_password=True)
            .create(
                {
                    "name": "Jane Smith",
                    "login": "jane.smith@example.com",
                    "partner_id": self.other_contact.id,
                    "group_ids": [(6, 0, [self.env.ref("base.group_portal").id])],
                }
            )
        )
        order = self.order.with_user(other_user)
        order.invalidate_recordset()
        with self.assertRaises(AccessError):
            order.read(["name"])

    def test_04_portal_orders_domain_includes_sale_contact(self):
        """The /my/orders and /my/quotes domains match the orders on which
        the user is the sale contact."""
        controller = CustomerPortal()
        orders_domain = controller._prepare_orders_domain(self.contact_person)
        orders = (
            self.env["sale.order"].with_user(self.portal_user).search(orders_domain)
        )
        self.assertIn(self.order, orders)

        quotation = self.order.copy({"sale_contact_partner_id": self.contact_person.id})
        quotation.action_quotation_sent()
        quotations_domain = controller._prepare_quotations_domain(self.contact_person)
        quotations = (
            self.env["sale.order"].with_user(self.portal_user).search(quotations_domain)
        )
        self.assertIn(quotation, quotations)
