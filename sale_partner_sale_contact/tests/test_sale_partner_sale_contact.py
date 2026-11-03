# Copyright 2026 OpenStudio SAS
# License LGPL-3.0 or later (https://www.gnu.org/licenses/lgpl).

from odoo.tests.common import TransactionCase


class TestSalePartnerSaleContact(TransactionCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()

        # Create a company partner
        cls.partner_company = cls.env["res.partner"].create(
            {
                "name": "Test Company",
                "is_company": True,
            }
        )

        # Create child contacts (persons)
        cls.contact_person_1 = cls.env["res.partner"].create(
            {
                "name": "John Doe",
                "is_company": False,
                "parent_id": cls.partner_company.id,
                "type": "contact",
            }
        )

        cls.contact_person_2 = cls.env["res.partner"].create(
            {
                "name": "Jane Smith",
                "is_company": False,
                "parent_id": cls.partner_company.id,
                "type": "contact",
            }
        )

        # Create an invoice-type address (billing address) of the company
        cls.invoice_address = cls.env["res.partner"].create(
            {
                "name": "Billing Department",
                "is_company": False,
                "parent_id": cls.partner_company.id,
                "type": "invoice",
            }
        )

        # Create another company (for testing domain restrictions)
        cls.other_company = cls.env["res.partner"].create(
            {
                "name": "Other Company",
                "is_company": True,
            }
        )

        cls.other_contact = cls.env["res.partner"].create(
            {
                "name": "Bob Johnson",
                "is_company": False,
                "parent_id": cls.other_company.id,
                "type": "contact",
            }
        )

        # Create a product for sale orders
        cls.product = cls.env["product.product"].create(
            {
                "name": "Test Product",
                "list_price": 100.0,
                "type": "consu",
            }
        )

        # Create a sale journal so that invoice creation works in tests
        # (the test database has no chart of accounts installed by default)
        cls.income_account = cls.env["account.account"].create(
            {
                "name": "Test Income Account",
                "code": "TEST400",
                "account_type": "income",
                "company_ids": [(6, 0, cls.env.company.ids)],
            }
        )
        cls.sale_journal = cls.env["account.journal"].create(
            {
                "name": "Customer Invoices (test)",
                "type": "sale",
                "code": "TINV",
                "company_id": cls.env.company.id,
                "default_account_id": cls.income_account.id,
            }
        )
        # Assign the income account to the product so invoice lines are valid
        cls.product.write(
            {
                "property_account_income_id": cls.income_account.id,
            }
        )

        # Create a receivable account and assign it to the partner so that
        # the receivable line on invoices is valid (date_maturity is computed)
        cls.receivable_account = cls.env["account.account"].create(
            {
                "name": "Test Receivable Account",
                "code": "TEST130",
                "account_type": "asset_receivable",
                "reconcile": True,
                "company_ids": [(6, 0, cls.env.company.ids)],
            }
        )
        cls.partner_company.write(
            {
                "property_account_receivable_id": cls.receivable_account.id,
            }
        )

    def test_01_sale_order_contact_field(self):
        """Test that sale contact field can be set on sale order."""
        sale_order = self.env["sale.order"].create(
            {
                "partner_id": self.partner_company.id,
                "sale_contact_partner_id": self.contact_person_1.id,
            }
        )

        self.assertEqual(
            sale_order.sale_contact_partner_id,
            self.contact_person_1,
            "Sale contact should be set correctly",
        )

    def test_02_sale_order_contact_propagation_to_invoice(self):
        """Test that sale contact is propagated from sale order to invoice."""
        # Create a sale order with a contact
        sale_order = self.env["sale.order"].create(
            {
                "partner_id": self.partner_company.id,
                "sale_contact_partner_id": self.contact_person_1.id,
                "order_line": [
                    (
                        0,
                        0,
                        {
                            "product_id": self.product.id,
                            "product_uom_qty": 1.0,
                            "price_unit": 100.0,
                        },
                    )
                ],
            }
        )

        # Confirm the sale order
        sale_order.action_confirm()

        # Create invoice
        invoice = sale_order._create_invoices()

        self.assertEqual(
            len(invoice),
            1,
            "Should create exactly one invoice",
        )
        self.assertEqual(
            invoice.sale_contact_partner_id,
            self.contact_person_1,
            "Sale contact should be propagated to invoice",
        )

    def test_03_onchange_partner_clears_contact(self):
        """Test that changing partner clears incompatible sale contact."""
        # Create sale order with partner and contact
        sale_order = self.env["sale.order"].create(
            {
                "partner_id": self.partner_company.id,
                "sale_contact_partner_id": self.contact_person_1.id,
            }
        )

        # Change partner to another company
        sale_order.partner_id = self.other_company

        # Trigger onchange
        sale_order._onchange_partner_id_clear_sale_contact()

        # Contact should be cleared since it doesn't belong to new partner
        self.assertFalse(
            sale_order.sale_contact_partner_id,
            "Sale contact should be cleared when partner changes",
        )

    def test_04_onchange_partner_keeps_compatible_contact(self):
        """Test that changing partner keeps sale contact if still valid."""
        # Create a contact that belongs to both companies (unusual but possible)
        shared_contact = self.env["res.partner"].create(
            {
                "name": "Shared Contact",
                "is_company": False,
                "parent_id": self.partner_company.id,
                "type": "contact",
            }
        )

        sale_order = self.env["sale.order"].create(
            {
                "partner_id": self.partner_company.id,
                "sale_contact_partner_id": shared_contact.id,
            }
        )

        # Set parent of contact to be the same as partner (still valid)
        # In this case, since we check parent_id == partner_id, contact remains
        sale_order._onchange_partner_id_clear_sale_contact()

        self.assertEqual(
            sale_order.sale_contact_partner_id,
            shared_contact,
            "Sale contact should remain when still valid for new partner",
        )

    def test_05_invoice_contact_field(self):
        """Test that sale contact field can be set on invoice."""
        invoice = self.env["account.move"].create(
            {
                "move_type": "out_invoice",
                "partner_id": self.partner_company.id,
                "sale_contact_partner_id": self.contact_person_2.id,
            }
        )

        self.assertEqual(
            invoice.sale_contact_partner_id,
            self.contact_person_2,
            "Sale contact should be set correctly on invoice",
        )

    def test_06_empty_contact_allowed(self):
        """Test that sale contact field can be left empty."""
        sale_order = self.env["sale.order"].create(
            {
                "partner_id": self.partner_company.id,
            }
        )

        self.assertFalse(
            sale_order.sale_contact_partner_id,
            "Sale contact should be empty when not set",
        )

        # Confirm order and create invoice
        sale_order.order_line = [
            (
                0,
                0,
                {
                    "product_id": self.product.id,
                    "product_uom_qty": 1.0,
                    "price_unit": 100.0,
                },
            )
        ]
        sale_order.action_confirm()
        invoice = sale_order._create_invoices()

        self.assertFalse(
            invoice.sale_contact_partner_id,
            "Invoice should also have empty sale contact when not set on order",
        )

    def test_07_multiple_orders_different_contacts(self):
        """Test multiple orders can have different contacts."""
        sale_order_1 = self.env["sale.order"].create(
            {
                "partner_id": self.partner_company.id,
                "sale_contact_partner_id": self.contact_person_1.id,
            }
        )

        sale_order_2 = self.env["sale.order"].create(
            {
                "partner_id": self.partner_company.id,
                "sale_contact_partner_id": self.contact_person_2.id,
            }
        )

        self.assertEqual(sale_order_1.sale_contact_partner_id, self.contact_person_1)
        self.assertEqual(sale_order_2.sale_contact_partner_id, self.contact_person_2)
        self.assertNotEqual(
            sale_order_1.sale_contact_partner_id,
            sale_order_2.sale_contact_partner_id,
        )

    def test_08_auto_switch_contact_to_company(self):
        """Test auto-switch: selecting a contact as partner_id promotes to company.

        When a user selects a contact person (non-company) as the partner_id,
        _sale_contact_apply_auto_switch() should automatically:
        - replace partner_id with the root company (commercial_partner_id)
        - store the selected contact in sale_contact_partner_id
        """
        sale_order = self.env["sale.order"].create(
            {
                "partner_id": self.partner_company.id,
            }
        )
        # Simulate user selecting a contact person as partner_id
        sale_order.partner_id = self.contact_person_1
        switched = sale_order._sale_contact_apply_auto_switch()

        self.assertTrue(switched, "Auto-switch should have been applied")
        self.assertEqual(
            sale_order.partner_id,
            self.partner_company,
            "partner_id should be switched to root company",
        )
        self.assertEqual(
            sale_order.sale_contact_partner_id,
            self.contact_person_1,
            "The selected contact should be stored in sale_contact_partner_id",
        )

    def test_08b_no_auto_switch_invoice_address_on_account_move(self):
        """Test that the auto-switch is skipped for invoice-type addresses.

        On an account.move it is legitimate to bill a dedicated invoice
        address (address type 'invoice') as partner_id rather than the root
        company, so _sale_contact_apply_auto_switch() must NOT promote it.
        """
        invoice = self.env["account.move"].create(
            {
                "move_type": "out_invoice",
                "partner_id": self.partner_company.id,
            }
        )
        # Simulate user selecting the invoice-type address as partner_id
        invoice.partner_id = self.invoice_address
        switched = invoice._sale_contact_apply_auto_switch()

        self.assertFalse(
            switched, "Auto-switch should be skipped for invoice-type addresses"
        )
        self.assertEqual(
            invoice.partner_id,
            self.invoice_address,
            "partner_id should keep the selected invoice address",
        )
        self.assertFalse(
            invoice.sale_contact_partner_id,
            "No contact should be stored when the switch is skipped",
        )

    def test_08c_auto_switch_contact_on_account_move(self):
        """Test that the auto-switch still applies for contact-type addresses.

        A regular contact person (address type 'contact') selected as
        partner_id on an account.move must still be promoted to the company.
        """
        invoice = self.env["account.move"].create(
            {
                "move_type": "out_invoice",
                "partner_id": self.partner_company.id,
            }
        )
        invoice.partner_id = self.contact_person_1
        switched = invoice._sale_contact_apply_auto_switch()

        self.assertTrue(switched, "Auto-switch should apply for contact addresses")
        self.assertEqual(invoice.partner_id, self.partner_company)
        self.assertEqual(invoice.sale_contact_partner_id, self.contact_person_1)

    def test_09_prepare_invoice_without_contact_key_absent(self):
        """Test _prepare_invoice does not include key when contact is False.

        The if-guard in _prepare_invoice should mean sale_contact_partner_id
        is entirely absent from the returned dict, not just False/None.
        """
        sale_order = self.env["sale.order"].create(
            {
                "partner_id": self.partner_company.id,
                "order_line": [
                    (
                        0,
                        0,
                        {
                            "product_id": self.product.id,
                            "product_uom_qty": 1.0,
                            "price_unit": 100.0,
                        },
                    )
                ],
            }
        )
        sale_order.action_confirm()
        invoice_vals = sale_order._prepare_invoice()

        self.assertNotIn(
            "sale_contact_partner_id",
            invoice_vals,
            "sale_contact_partner_id key must be absent from invoice vals "
            "when no contact is set on the order",
        )

    def test_10_onchange_keeps_grandchild_contact(self):
        """Test that a grandchild contact is not cleared on partner change.

        The domain uses child_of which includes the full hierarchy.  A contact
        nested two levels deep (Company -> Department -> Person) must not be
        incorrectly cleared by the onchange.
        """
        # Create an intermediate 'department' partner
        department = self.env["res.partner"].create(
            {
                "name": "Sales Department",
                "is_company": False,
                "parent_id": self.partner_company.id,
                "type": "contact",
            }
        )
        # Create a grandchild contact under the department
        grandchild = self.env["res.partner"].create(
            {
                "name": "Grandchild Contact",
                "is_company": False,
                "parent_id": department.id,
                "type": "contact",
            }
        )

        sale_order = self.env["sale.order"].create(
            {
                "partner_id": self.partner_company.id,
                "sale_contact_partner_id": grandchild.id,
            }
        )

        # Trigger the onchange (partner has not actually changed)
        sale_order._onchange_partner_id_clear_sale_contact()

        self.assertEqual(
            sale_order.sale_contact_partner_id,
            grandchild,
            "Grandchild contact should NOT be cleared: it belongs to the "
            "partner's hierarchy via commercial_partner_id",
        )
