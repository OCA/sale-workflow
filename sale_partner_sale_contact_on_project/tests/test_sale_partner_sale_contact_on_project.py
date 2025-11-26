# Copyright 2026 OpenStudio SAS
# License LGPL-3.0 or later (https://www.gnu.org/licenses/lgpl).

from odoo.tests.common import TransactionCase


class TestSalePartnerSaleContactOnProject(TransactionCase):
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

        # Create a child contact (person)
        cls.contact_person = cls.env["res.partner"].create(
            {
                "name": "John Doe",
                "is_company": False,
                "parent_id": cls.partner_company.id,
                "type": "contact",
            }
        )

        # Create a product that creates a project
        cls.product_service = cls.env["product.product"].create(
            {
                "name": "Service Product",
                "type": "service",
                "invoice_policy": "delivery",
                "service_tracking": "task_in_project",
            }
        )

    def test_01_sale_contact_propagation_to_project(self):
        """Test that sale contact is propagated from sale order to project."""
        # Create a sale order with sale contact and service product
        sale_order = self.env["sale.order"].create(
            {
                "partner_id": self.partner_company.id,
                "sale_contact_partner_id": self.contact_person.id,
                "order_line": [
                    (
                        0,
                        0,
                        {
                            "product_id": self.product_service.id,
                            "product_uom_qty": 1.0,
                            "price_unit": 100.0,
                        },
                    )
                ],
            }
        )

        # Confirm the sale order (this should create a project)
        sale_order.action_confirm()

        # Find the created project
        project = self.env["project.project"].search(
            [("sale_order_id", "=", sale_order.id)], limit=1
        )

        # Verify project was created
        self.assertTrue(project, "A project should have been created")

        # Verify sale contact was propagated
        self.assertEqual(
            project.sale_contact_partner_id,
            self.contact_person,
            "Sale contact should be propagated to the project",
        )

    def test_02_project_field_manual_set(self):
        """Test that sale contact field can be set manually on a project."""
        project = self.env["project.project"].create(
            {
                "name": "Test Project",
                "partner_id": self.partner_company.id,
                "sale_contact_partner_id": self.contact_person.id,
            }
        )

        self.assertEqual(
            project.sale_contact_partner_id,
            self.contact_person,
            "Sale contact should be set on project",
        )

    def test_03_empty_contact_allowed(self):
        """Test that sale contact can be left empty on project."""
        project = self.env["project.project"].create(
            {
                "name": "Test Project",
                "partner_id": self.partner_company.id,
            }
        )

        self.assertFalse(
            project.sale_contact_partner_id,
            "Sale contact should be empty when not set",
        )

    def test_04_sale_order_without_contact_creates_project_without_contact(self):
        """Test that a sale order without contact creates a project without contact."""
        # Create a sale order WITHOUT sale contact
        sale_order = self.env["sale.order"].create(
            {
                "partner_id": self.partner_company.id,
                "order_line": [
                    (
                        0,
                        0,
                        {
                            "product_id": self.product_service.id,
                            "product_uom_qty": 1.0,
                            "price_unit": 100.0,
                        },
                    )
                ],
            }
        )

        # Confirm the sale order
        sale_order.action_confirm()

        # Find the created project
        project = self.env["project.project"].search(
            [("sale_order_id", "=", sale_order.id)], limit=1
        )

        # Verify project was created without sale contact
        self.assertTrue(project, "A project should have been created")
        self.assertFalse(
            project.sale_contact_partner_id,
            "Project should not have a sale contact",
        )

    def test_05_auto_switch_contact_to_company_on_project(self):
        """Test auto-switch on project.project: contact person → root company.

        When a user selects a contact person as partner_id on a project,
        _onchange_partner_id_sale_contact_auto_switch() should automatically:
        - replace partner_id with the root company (commercial_partner_id)
        - store the selected contact in sale_contact_partner_id
        """
        project = self.env["project.project"].create(
            {
                "name": "Test Project",
                "partner_id": self.partner_company.id,
            }
        )
        # Simulate user selecting a contact person as partner_id
        project.partner_id = self.contact_person
        project._onchange_partner_id_sale_contact_auto_switch()

        self.assertEqual(
            project.partner_id,
            self.partner_company,
            "partner_id should be switched to root company",
        )
        self.assertEqual(
            project.sale_contact_partner_id,
            self.contact_person,
            "The selected contact should be stored in sale_contact_partner_id",
        )
