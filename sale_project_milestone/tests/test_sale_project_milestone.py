# Copyright 2025 Innovyou
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).

from odoo.exceptions import ValidationError
from odoo.tests import Form, tagged
from odoo.tests.common import TransactionCase


@tagged("post_install", "-at_install")
class TestSaleProjectMilestone(TransactionCase):
    """Test suite for sale_project_milestone module"""

    @classmethod
    def setUpClass(cls):
        super().setUpClass()

        # Create a partner
        cls.partner = cls.env["res.partner"].create(
            {
                "name": "Test Customer",
            }
        )

        # Create a service product with milestone_project tracking
        cls.product_milestone = cls.env["product.product"].create(
            {
                "name": "Milestone Service",
                "type": "service",
                "service_tracking": "milestone_project",
                "invoice_policy": "order",
            }
        )

        # Create a service product with milestone invoicing
        cls.product_milestone_invoicing = cls.env["product.product"].create(
            {
                "name": "Milestone Invoicing Service",
                "type": "service",
                "service_tracking": "milestone_project",
                "service_policy": "delivered_milestones",
                "invoice_policy": "delivery",
            }
        )

        # Create a project template
        cls.project_template = cls.env["project.project"].create(
            {
                "name": "Template Project",
                "allow_milestones": True,
                "allow_timesheets": True,
            }
        )

        # Add tasks to template
        cls.env["project.task"].create(
            {
                "name": "Template Task 1",
                "project_id": cls.project_template.id,
            }
        )
        cls.env["project.task"].create(
            {
                "name": "Template Task 2",
                "project_id": cls.project_template.id,
            }
        )

        # Create product with template
        cls.product_with_template = cls.env["product.product"].create(
            {
                "name": "Service with Template",
                "type": "service",
                "service_tracking": "milestone_project",
                "project_template_id": cls.project_template.id,
                "invoice_policy": "order",
            }
        )

        # Create a service product without tracking (for testing manual linking)
        cls.product_no_tracking = cls.env["product.product"].create(
            {
                "name": "Service No Tracking",
                "type": "service",
                "service_tracking": "no",
                "invoice_policy": "order",
            }
        )

        # Create an existing project for testing
        cls.existing_project = cls.env["project.project"].create(
            {
                "name": "Existing Project",
                "partner_id": cls.partner.id,
                "allow_milestones": True,
                "allow_timesheets": True,
            }
        )

        # Create an existing milestone
        cls.existing_milestone = cls.env["project.milestone"].create(
            {
                "name": "Existing Milestone",
                "project_id": cls.existing_project.id,
            }
        )

    def _create_sale_order(self, partner=None):
        """Helper method to create a sale order"""
        if partner is None:
            partner = self.partner
        return self.env["sale.order"].create(
            {
                "partner_id": partner.id,
            }
        )

    def test_01_create_project_automatically(self):
        """Test Option A: Create new project automatically when no project is selected"""
        sale_order = self._create_sale_order()

        # Create order line without selecting project
        order_line = self.env["sale.order.line"].create(
            {
                "order_id": sale_order.id,
                "product_id": self.product_milestone.id,
                "product_uom_qty": 1,
            }
        )

        self.assertFalse(order_line.project_id, "Project should not be set initially")
        self.assertFalse(order_line.task_id, "Task should not be created")

        # Confirm the order
        sale_order.action_confirm()

        # Check that project and milestone were created
        self.assertTrue(order_line.project_id, "Project should be created")
        self.assertEqual(
            order_line.project_id.name,
            sale_order.name,
            "Project name should match sale order",
        )
        self.assertTrue(order_line.project_id.allow_milestones)

        # Check milestone creation
        milestone = self.env["project.milestone"].search(
            [("sale_line_id", "=", order_line.id)]
        )
        self.assertEqual(len(milestone), 1, "One milestone should be created")
        self.assertEqual(milestone.project_id, order_line.project_id)
        self.assertEqual(milestone.name, order_line.name)
        self.assertEqual(milestone.quantity_percentage, 1.0)

    def test_02_add_milestone_to_existing_project(self):
        """Test Option B: Add new milestone to existing project"""
        sale_order = self._create_sale_order()

        # Create order line with existing project selected
        order_line = self.env["sale.order.line"].create(
            {
                "order_id": sale_order.id,
                "product_id": self.product_milestone.id,
                "product_uom_qty": 1,
                "existing_project_id": self.existing_project.id,
            }
        )

        # Confirm the order
        sale_order.action_confirm()

        # Check that existing project is used
        self.assertEqual(
            order_line.project_id, self.existing_project, "Should use existing project"
        )

        # Check milestone creation in existing project
        milestone = self.env["project.milestone"].search(
            [
                ("sale_line_id", "=", order_line.id),
                ("project_id", "=", self.existing_project.id),
            ]
        )
        self.assertEqual(len(milestone), 1, "One milestone should be created")
        self.assertEqual(milestone.project_id, self.existing_project)
        self.assertEqual(milestone.quantity_percentage, 1.0)

    def test_03_link_existing_milestone(self):
        """Test Option C: Link existing milestone directly"""
        sale_order = self._create_sale_order()

        # Create order line with existing project and milestone
        order_line = self.env["sale.order.line"].create(
            {
                "order_id": sale_order.id,
                "product_id": self.product_milestone.id,
                "product_uom_qty": 1,
                "existing_project_id": self.existing_project.id,
                "existing_milestone_id": self.existing_milestone.id,
            }
        )

        # Confirm the order
        sale_order.action_confirm()

        # Check that existing milestone is linked
        self.assertEqual(
            self.existing_milestone.sale_line_id,
            order_line,
            "Milestone should be linked",
        )
        self.assertEqual(
            order_line.project_id, self.existing_project, "Should use existing project"
        )
        self.assertEqual(self.existing_milestone.quantity_percentage, 1.0)

        # No new milestone should be created
        milestones = self.env["project.milestone"].search(
            [
                ("sale_line_id", "=", order_line.id),
                ("project_id", "=", self.existing_project.id),
            ]
        )
        self.assertEqual(
            len(milestones), 1, "Only the existing milestone should be linked"
        )
        self.assertEqual(milestones, self.existing_milestone)

    def test_04_project_template_usage(self):
        """Test project creation from template"""
        sale_order = self._create_sale_order()

        # Create order line with product that has template
        order_line = self.env["sale.order.line"].create(
            {
                "order_id": sale_order.id,
                "product_id": self.product_with_template.id,
                "product_uom_qty": 1,
            }
        )

        # Confirm the order
        sale_order.action_confirm()

        # Check that project was created from template
        self.assertTrue(order_line.project_id, "Project should be created")
        self.assertNotEqual(
            order_line.project_id,
            self.project_template,
            "Should not be the template itself",
        )
        self.assertTrue(order_line.project_id.allow_milestones)

        # Check that tasks were copied
        tasks = self.env["project.task"].search(
            [("project_id", "=", order_line.project_id.id)]
        )
        template_tasks = self.env["project.task"].search(
            [("project_id", "=", self.project_template.id)]
        )
        self.assertEqual(
            len(tasks),
            len(template_tasks),
            "Tasks should be copied from template",
        )

        # Check milestone creation
        milestone = self.env["project.milestone"].search(
            [("sale_line_id", "=", order_line.id)]
        )
        self.assertEqual(len(milestone), 1, "One milestone should be created")

    def test_05_link_milestone_after_confirmation(self):
        """Test linking existing milestone to confirmed sale order
        with product tracking change"""
        sale_order = self._create_sale_order()

        # Create a new milestone for this test
        new_milestone = self.env["project.milestone"].create(
            {
                "name": "New Milestone for Linking",
                "project_id": self.existing_project.id,
            }
        )

        # Create order line with product that has no tracking
        order_line = self.env["sale.order.line"].create(
            {
                "order_id": sale_order.id,
                "product_id": self.product_no_tracking.id,
                "product_uom_qty": 1,
            }
        )

        # Confirm order - nothing should be created
        sale_order.action_confirm()
        self.assertFalse(order_line.project_id, "No project should be created")
        self.assertFalse(order_line.task_id, "No task should be created")

        # Change product's service tracking to milestone_project
        self.product_no_tracking.service_tracking = "milestone_project"

        # Set the existing project and milestone on the order line
        order_line.write(
            {
                "existing_project_id": self.existing_project.id,
                "existing_milestone_id": new_milestone.id,
            }
        )

        # Call the link action
        order_line.action_link_existing_milestone()

        # Check that milestone is linked
        self.assertEqual(new_milestone.sale_line_id, order_line)
        self.assertEqual(order_line.project_id, self.existing_project)
        self.assertEqual(new_milestone.quantity_percentage, 1.0)

        # Reset product tracking for other tests
        self.product_no_tracking.service_tracking = "no"

    def test_06_link_milestone_validation_no_milestone_selected(self):
        """Test validation when no milestone is selected"""
        sale_order = self._create_sale_order()

        # Create order line with product that has no tracking
        order_line = self.env["sale.order.line"].create(
            {
                "order_id": sale_order.id,
                "product_id": self.product_no_tracking.id,
                "product_uom_qty": 1,
            }
        )

        # Confirm order - nothing should be created
        sale_order.action_confirm()
        self.assertFalse(order_line.project_id, "No project should be created")

        # Change product's service tracking to milestone_project
        self.product_no_tracking.service_tracking = "milestone_project"

        # Try to link without selecting milestone
        with self.assertRaises(ValidationError) as cm:
            order_line.action_link_existing_milestone()

        self.assertIn("select an existing milestone", str(cm.exception).lower())

        # Reset product tracking for other tests
        self.product_no_tracking.service_tracking = "no"

    def test_07_link_milestone_validation_already_linked(self):
        """Test validation when milestone is already linked"""
        sale_order1 = self._create_sale_order()
        sale_order2 = self._create_sale_order()

        # Create two order lines with product that has no tracking
        order_line1 = self.env["sale.order.line"].create(
            {
                "order_id": sale_order1.id,
                "product_id": self.product_no_tracking.id,
                "product_uom_qty": 1,
            }
        )

        order_line2 = self.env["sale.order.line"].create(
            {
                "order_id": sale_order2.id,
                "product_id": self.product_no_tracking.id,
                "product_uom_qty": 1,
            }
        )

        # Confirm both orders - nothing should be created
        sale_order1.action_confirm()
        sale_order2.action_confirm()
        self.assertFalse(order_line1.project_id, "No project should be created")
        self.assertFalse(order_line2.project_id, "No project should be created")

        # Change product's service tracking to milestone_project
        self.product_no_tracking.service_tracking = "milestone_project"

        # Create a milestone and link it to first order line
        milestone = self.env["project.milestone"].create(
            {
                "name": "Test Milestone",
                "project_id": self.existing_project.id,
            }
        )

        order_line1.existing_project_id = self.existing_project
        order_line1.existing_milestone_id = milestone
        order_line1.action_link_existing_milestone()

        # Try to link same milestone to second order line
        order_line2.existing_project_id = self.existing_project
        order_line2.existing_milestone_id = milestone

        with self.assertRaises(ValidationError) as cm:
            order_line2.action_link_existing_milestone()

        self.assertIn("already linked", str(cm.exception).lower())

        # Reset product tracking for other tests
        self.product_no_tracking.service_tracking = "no"

    def test_08_analytic_line_registration_draft_invoice(self):
        """Test analytic line registration for draft invoices"""
        sale_order = self._create_sale_order()

        # Create order line with product that has no tracking
        order_line = self.env["sale.order.line"].create(
            {
                "order_id": sale_order.id,
                "product_id": self.product_no_tracking.id,
                "product_uom_qty": 1,
                "price_unit": 100.0,
            }
        )

        # Confirm order - nothing should be created
        sale_order.action_confirm()
        self.assertFalse(order_line.project_id, "No project should be created")

        # Create invoice
        invoice = sale_order._create_invoices()
        self.assertEqual(invoice.state, "draft")

        # Change product's service tracking to milestone_project
        self.product_no_tracking.service_tracking = "milestone_project"

        # Link existing milestone after invoice creation
        milestone = self.env["project.milestone"].create(
            {
                "name": "Post Invoice Milestone",
                "project_id": self.existing_project.id,
            }
        )

        order_line.existing_project_id = self.existing_project
        order_line.existing_milestone_id = milestone
        order_line.action_link_existing_milestone()

        # Check that invoice line has analytic distribution
        invoice_line = invoice.invoice_line_ids.filtered(
            lambda l: l.sale_line_ids == order_line
        )
        self.assertTrue(invoice_line)
        self.assertTrue(invoice_line.analytic_distribution)
        # Convert keys to str for consistent comparison
        analytic_dist_keys = {str(k) for k in invoice_line.analytic_distribution.keys()}
        self.assertIn(
            str(self.existing_project.analytic_account_id.id),
            analytic_dist_keys,
        )

        # Reset product tracking for other tests
        self.product_no_tracking.service_tracking = "no"

    def test_09_analytic_line_registration_posted_invoice(self):
        """Test analytic line registration for posted invoices"""
        sale_order = self._create_sale_order()

        # Create order line with product that has no tracking
        order_line = self.env["sale.order.line"].create(
            {
                "order_id": sale_order.id,
                "product_id": self.product_no_tracking.id,
                "product_uom_qty": 1,
                "price_unit": 100.0,
            }
        )

        # Confirm order - nothing should be created
        sale_order.action_confirm()
        self.assertFalse(order_line.project_id, "No project should be created")

        # Create and post invoice
        invoice = sale_order._create_invoices()
        invoice.action_post()
        self.assertEqual(invoice.state, "posted")

        # Change product's service tracking to milestone_project
        self.product_no_tracking.service_tracking = "milestone_project"

        # Link existing milestone after invoice posting
        milestone = self.env["project.milestone"].create(
            {
                "name": "Post Invoice Milestone",
                "project_id": self.existing_project.id,
            }
        )

        order_line.existing_project_id = self.existing_project
        order_line.existing_milestone_id = milestone
        order_line.action_link_existing_milestone()

        # Check that analytic lines were created
        invoice_line = invoice.invoice_line_ids.filtered(
            lambda l: l.sale_line_ids == order_line
        )
        analytic_lines = self.env["account.analytic.line"].search(
            [
                ("move_line_id", "=", invoice_line.id),
                ("account_id", "=", self.existing_project.analytic_account_id.id),
            ]
        )
        self.assertTrue(analytic_lines, "Analytic lines should be created")
        self.assertEqual(len(analytic_lines), 1)
        self.assertEqual(analytic_lines.category, "invoice")

        # Reset product tracking for other tests
        self.product_no_tracking.service_tracking = "no"

    def test_10_milestone_based_invoicing(self):
        """Test milestone-based invoicing workflow"""
        sale_order = self._create_sale_order()

        order_line = self.env["sale.order.line"].create(
            {
                "order_id": sale_order.id,
                "product_id": self.product_milestone_invoicing.id,
                "product_uom_qty": 10,
                "price_unit": 100.0,
            }
        )

        # Confirm order
        sale_order.action_confirm()

        # Check that milestone was created
        milestone = self.env["project.milestone"].search(
            [("sale_line_id", "=", order_line.id)]
        )
        self.assertTrue(milestone)

        # Initially, delivered quantity should be 0
        self.assertEqual(order_line.qty_delivered, 0.0)

        # Mark milestone as reached
        milestone.is_reached = True

        # Delivered quantity should be updated
        self.assertEqual(order_line.qty_delivered, 10.0)

        # Create invoice
        invoice = sale_order._create_invoices()
        self.assertTrue(invoice)

        # Check invoice line has analytic distribution
        invoice_line = invoice.invoice_line_ids.filtered(
            lambda l: l.sale_line_ids == order_line
        )
        self.assertTrue(invoice_line.analytic_distribution)
        # Convert keys to str for consistent comparison
        analytic_dist_keys = {str(k) for k in invoice_line.analytic_distribution.keys()}
        self.assertIn(
            str(order_line.project_id.analytic_account_id.id),
            analytic_dist_keys,
        )

    def test_11_product_tooltip_computation(self):
        """Test product tooltip computation for different service policies"""
        # Test with delivered_milestones
        product_delivered = self.env["product.template"].create(
            {
                "name": "Test Delivered",
                "type": "service",
                "service_tracking": "milestone_project",
                "service_policy": "delivered_milestones",
            }
        )
        product_delivered._compute_product_tooltip()
        self.assertIn(
            "Invoice your milestones when they are reached",
            product_delivered.product_tooltip,
        )

        # Test with ordered_prepaid
        product_prepaid = self.env["product.template"].create(
            {
                "name": "Test Prepaid",
                "type": "service",
                "service_tracking": "milestone_project",
                "service_policy": "ordered_prepaid",
            }
        )
        product_prepaid._compute_product_tooltip()
        self.assertIn(
            "Invoice ordered quantities as soon as", product_prepaid.product_tooltip
        )

        # Test with delivered_manual
        product_manual = self.env["product.template"].create(
            {
                "name": "Test Manual",
                "type": "service",
                "service_tracking": "milestone_project",
                "service_policy": "delivered_manual",
            }
        )
        product_manual._compute_product_tooltip()
        self.assertIn(
            "delivered (set the quantity by hand)", product_manual.product_tooltip
        )

    def test_13_onchange_existing_project(self):
        """Test onchange when existing_project_id changes"""
        order_form = Form(self.env["sale.order"])
        order_form.partner_id = self.partner

        with order_form.order_line.new() as line:
            line.product_id = self.product_milestone
            line.product_uom_qty = 1

            # Set project and milestone
            line.existing_project_id = self.existing_project
            line.existing_milestone_id = self.existing_milestone

            # Change project - milestone should be reset
            other_project = self.env["project.project"].create(
                {
                    "name": "Other Project",
                    "allow_milestones": True,
                    "allow_timesheets": True,
                }
            )
            line.existing_project_id = other_project

        sale_order = order_form.save()
        order_line = sale_order.order_line[0]

        self.assertFalse(
            order_line.existing_milestone_id,
            "Milestone should be reset when project changes",
        )

    def test_14_onchange_existing_milestone(self):
        """Test onchange when existing_milestone_id is set"""
        order_form = Form(self.env["sale.order"])
        order_form.partner_id = self.partner

        with order_form.order_line.new() as line:
            line.product_id = self.product_milestone
            line.product_uom_qty = 1

            # Set milestone - project should be auto-filled
            line.existing_milestone_id = self.existing_milestone

        sale_order = order_form.save()
        order_line = sale_order.order_line[0]

        self.assertEqual(
            order_line.existing_project_id,
            self.existing_project,
            "Project should be set from milestone",
        )

    def test_15_compute_show_project_milestone_field(self):
        """Test computation of show_project_milestone_field"""
        sale_order = self._create_sale_order()

        # Line with milestone_project product
        order_line_milestone = self.env["sale.order.line"].create(
            {
                "order_id": sale_order.id,
                "product_id": self.product_milestone.id,
                "product_uom_qty": 1,
            }
        )
        self.assertTrue(order_line_milestone.show_project_milestone_field)

        # Line with different product type
        normal_product = self.env["product.product"].create(
            {
                "name": "Normal Product",
                "type": "consu",
            }
        )
        order_line_normal = self.env["sale.order.line"].create(
            {
                "order_id": sale_order.id,
                "product_id": normal_product.id,
                "product_uom_qty": 1,
            }
        )
        self.assertFalse(order_line_normal.show_project_milestone_field)

    def test_16_compute_is_product_milestone(self):
        """Test computation of is_product_milestone on sale order"""
        sale_order = self._create_sale_order()

        # Add line with milestone_project
        self.env["sale.order.line"].create(
            {
                "order_id": sale_order.id,
                "product_id": self.product_milestone.id,
                "product_uom_qty": 1,
            }
        )

        self.assertTrue(
            sale_order.is_product_milestone,
            "is_product_milestone should be True",
        )

    def test_17_milestone_quantity_percentage_onchange(self):
        """Test milestone quantity_percentage is set on sale_line_id change"""
        milestone = self.env["project.milestone"].create(
            {
                "name": "Test Milestone",
                "project_id": self.existing_project.id,
            }
        )

        sale_order = self._create_sale_order()
        order_line = self.env["sale.order.line"].create(
            {
                "order_id": sale_order.id,
                "product_id": self.product_milestone.id,
                "product_uom_qty": 1,
            }
        )

        # Trigger onchange
        milestone.sale_line_id = order_line
        milestone._onchange_sale_line_id()

        self.assertEqual(milestone.quantity_percentage, 1.0)

    def test_18_prepare_invoice_line_with_analytic(self):
        """Test invoice line preparation includes analytic distribution"""
        sale_order = self._create_sale_order()

        order_line = self.env["sale.order.line"].create(
            {
                "order_id": sale_order.id,
                "product_id": self.product_milestone.id,
                "product_uom_qty": 1,
                "price_unit": 100.0,
                "existing_project_id": self.existing_project.id,
            }
        )

        sale_order.action_confirm()

        # Prepare invoice line values
        invoice_values = order_line._prepare_invoice_line()

        # Check that analytic distribution is set
        self.assertIn("analytic_distribution", invoice_values)
        # Convert keys to str for consistent comparison
        analytic_dist_keys = {
            str(k) for k in invoice_values["analytic_distribution"].keys()
        }
        self.assertIn(
            str(self.existing_project.analytic_account_id.id),
            analytic_dist_keys,
        )

    def test_19_onchange_service_tracking_product_template(self):
        """Test onchange of service_tracking clears project_id"""
        # Create product with service type first
        product_tmpl = self.env["product.template"].create(
            {
                "name": "Test Product",
                "type": "service",
            }
        )

        # Use Form to test onchange behavior
        product_form = Form(product_tmpl)

        # Set service_tracking to task_global_project first to make project_id visible
        product_form.service_tracking = "task_global_project"

        # Now set project_id
        project = self.env["project.project"].create({"name": "Test Project"})
        product_form.project_id = project

        # Change to milestone_project - project should be cleared
        product_form.service_tracking = "milestone_project"
        product = product_form.save()

        self.assertFalse(product.project_id, "Project should be cleared")

    def test_21_multiple_milestones_same_project(self):
        """Test creating multiple sale order lines with milestones in same project"""
        sale_order = self._create_sale_order()

        # Create two order lines for same project
        order_line1 = self.env["sale.order.line"].create(
            {
                "order_id": sale_order.id,
                "product_id": self.product_milestone.id,
                "product_uom_qty": 1,
                "existing_project_id": self.existing_project.id,
            }
        )

        order_line2 = self.env["sale.order.line"].create(
            {
                "order_id": sale_order.id,
                "product_id": self.product_milestone.id,
                "product_uom_qty": 1,
                "existing_project_id": self.existing_project.id,
            }
        )

        sale_order.action_confirm()

        # Both should use same project
        self.assertEqual(order_line1.project_id, self.existing_project)
        self.assertEqual(order_line2.project_id, self.existing_project)

        # But have different milestones
        milestone1 = self.env["project.milestone"].search(
            [("sale_line_id", "=", order_line1.id)]
        )
        milestone2 = self.env["project.milestone"].search(
            [("sale_line_id", "=", order_line2.id)]
        )

        self.assertEqual(len(milestone1), 1)
        self.assertEqual(len(milestone2), 1)
        self.assertNotEqual(milestone1, milestone2)
        self.assertEqual(milestone1.project_id, self.existing_project)
        self.assertEqual(milestone2.project_id, self.existing_project)

    def test_22_message_posting_on_milestone_creation(self):
        """Test that messages are posted on sale order when milestones
        are created"""
        sale_order = self._create_sale_order()

        self.env["sale.order.line"].create(
            {
                "order_id": sale_order.id,
                "product_id": self.product_milestone.id,
                "product_uom_qty": 1,
            }
        )

        # Confirm order
        sale_order.action_confirm()

        # Check that message was posted
        messages = sale_order.message_ids
        milestone_messages = messages.filtered(
            lambda m: "Milestone Created" in (m.body or "")
        )
        self.assertTrue(
            milestone_messages, "Milestone creation message should be posted"
        )

    def test_23_message_posting_on_milestone_linking(self):
        """Test that messages are posted when linking existing milestone"""
        sale_order = self._create_sale_order()

        milestone = self.env["project.milestone"].create(
            {
                "name": "Test Milestone",
                "project_id": self.existing_project.id,
            }
        )

        order_line = self.env["sale.order.line"].create(
            {
                "order_id": sale_order.id,
                "product_id": self.product_milestone.id,
                "product_uom_qty": 1,
            }
        )

        sale_order.action_confirm()

        # Link milestone
        order_line.existing_project_id = self.existing_project
        order_line.existing_milestone_id = milestone
        order_line.action_link_existing_milestone()

        # Check that message was posted
        messages = sale_order.message_ids
        link_messages = messages.filtered(
            lambda m: "linked to project" in (m.body or "")
        )
        self.assertTrue(link_messages, "Milestone linking message should be posted")
