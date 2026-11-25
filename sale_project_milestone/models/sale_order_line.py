# Copyright 2025 Innovyou
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).

from odoo import _, api, fields, models
from odoo.exceptions import ValidationError


class SaleOrderLine(models.Model):
    _inherit = "sale.order.line"

    existing_project_id = fields.Many2one(
        "project.project",
        string="Project",
        help="Select an existing project or leave empty to create a new one",
        domain="[('company_id', '=', company_id)]",
        copy=False,
    )
    existing_milestone_id = fields.Many2one(
        "project.milestone",
        string="Existing Milestone",
        help="Link this sale order line to an existing milestone",
        domain="[('project_id', '=', existing_project_id), ('sale_line_id', '=', False)]",
        copy=False,
    )
    show_project_milestone_field = fields.Boolean(
        compute="_compute_show_project_milestone_field"
    )

    @api.depends("product_id.service_tracking")
    def _compute_show_project_milestone_field(self):
        for line in self:
            line.show_project_milestone_field = (
                line.product_id.service_tracking == "milestone_project"
            )

    @api.onchange("existing_project_id")
    def _onchange_existing_project_id(self):
        """Reset existing_milestone_id when project changes"""
        if self.existing_milestone_id and (
            not self.existing_project_id
            or self.existing_milestone_id.project_id != self.existing_project_id
        ):
            self.existing_milestone_id = False

    @api.onchange("existing_milestone_id")
    def _onchange_existing_milestone_id(self):
        """Set project from milestone if milestone is selected"""
        if self.existing_milestone_id:
            self.existing_project_id = self.existing_milestone_id.project_id

    def _timesheet_service_generation(self):
        """Override to handle milestone_project tracking"""
        # Handle milestone project lines
        milestone_project_lines = self.filtered(
            lambda sol: sol.is_service
            and sol.product_id.service_tracking == "milestone_project"
        )

        for line in milestone_project_lines:
            # If existing milestone is selected, link it
            if (
                line.existing_milestone_id
                and not line.existing_milestone_id.sale_line_id
            ):
                line.existing_milestone_id.write(
                    {
                        "sale_line_id": line.id,
                        "quantity_percentage": 1.0,
                    }
                )
                # Link the project
                if not line.project_id:
                    line.project_id = line.existing_milestone_id.project_id
            else:
                # Determine or create the project
                project = line.existing_project_id
                if not project:
                    # Create a new project (like project_only flow)
                    project = line._timesheet_create_project()
                    line.existing_project_id = project
                elif not line.project_id:
                    # Link the existing project
                    line.project_id = project

                # Create milestone in the project
                milestone = line._generate_milestone(project)
                if milestone:
                    line.existing_milestone_id = milestone

        # Call super for other lines
        return super(
            SaleOrderLine, self - milestone_project_lines
        )._timesheet_service_generation()

    def _generate_milestone(self, project=None):
        """Override to handle milestone creation in project"""
        self.ensure_one()
        if not project:
            project = self.project_id or self.order_id.project_id

        if not project:
            return super()._generate_milestone()

        # Always create milestone when service_tracking is milestone_project
        milestone = self.env["project.milestone"].create(
            {
                "name": self.name,
                "project_id": project.id,
                "sale_line_id": self.id,
                "quantity_percentage": 1.0,
            }
        )

        # Post message on sale order
        msg_body = _(
            "Milestone Created (%(product)s) in project %(project)s: %(milestone)s"
        ) % {
            "product": self.product_id.name,
            "project": project._get_html_link(),
            "milestone": milestone._get_html_link(),
        }
        self.order_id.message_post(body=msg_body)

        return milestone

    def _prepare_invoice_line(self, **optional_values):
        """Ensure analytic account is set from project"""
        values = super()._prepare_invoice_line(**optional_values)

        # If milestone_project and project is set, use its analytic account
        if (
            self.product_id.service_tracking == "milestone_project"
            and self.project_id
            and not values.get("analytic_distribution")
        ):
            if self.project_id.analytic_account_id:
                values["analytic_distribution"] = {
                    self.project_id.analytic_account_id.id: 100
                }

        return values

    def action_link_existing_milestone(self):
        """Action to link an existing milestone to confirmed sale order lines"""
        self.ensure_one()
        if not self.existing_milestone_id:
            raise ValidationError(_("Please select an existing milestone first."))

        if self.existing_milestone_id.sale_line_id:
            raise ValidationError(
                _(
                    "The selected milestone is already linked to another "
                    "sale order line: %s"
                )
                % (self.existing_milestone_id.sale_line_id.name,)
            )

        # Link the milestone
        self.existing_milestone_id.write(
            {
                "sale_line_id": self.id,
                "quantity_percentage": 1.0,
            }
        )

        # Link the project
        if not self.project_id:
            self.project_id = self.existing_milestone_id.project_id

        # Register analytic lines for existing invoices if any
        self._register_analytic_lines_for_existing_invoices()

        # Post message on sale order chatter
        msg_body = _(
            "Line (%(product)s) linked to project %(project)s: milestone %(milestone)s"
        ) % {
            "product": self.product_id.name,
            "project": self.existing_milestone_id.project_id._get_html_link(),
            "milestone": self.existing_milestone_id._get_html_link(),
        }
        self.order_id.message_post(body=msg_body)

        return True

    def _register_analytic_lines_for_existing_invoices(self):
        """Register analytic lines on the project for existing invoices"""
        self.ensure_one()
        if not self.project_id or not self.project_id.analytic_account_id:
            return

        analytic_account = self.project_id.analytic_account_id

        # Get invoice lines excluding section headers and notes
        invoice_lines = self.invoice_lines.filtered(
            lambda l: l.display_type not in ("line_section", "line_note")
        )

        # Handle draft invoices - update analytic_distribution directly
        draft_invoice_lines = invoice_lines.filtered(
            lambda l: l.move_id.state == "draft"
        )
        for inv_line in draft_invoice_lines:
            if (
                not inv_line.analytic_distribution
                or analytic_account.id not in inv_line.analytic_distribution
            ):
                inv_line.analytic_distribution = {analytic_account.id: 100}

        # Handle posted invoices - update analytic_distribution and create analytic lines
        posted_invoice_lines = invoice_lines.filtered(
            lambda l: l.move_id.state == "posted"
        )

        for inv_line in posted_invoice_lines:
            # Update analytic_distribution on the invoice line
            if (
                not inv_line.analytic_distribution
                or analytic_account.id not in inv_line.analytic_distribution
            ):
                inv_line.analytic_distribution = {analytic_account.id: 100}

            # Check if analytic lines already exist for this account
            existing_lines = self.env["account.analytic.line"].search(
                [
                    ("move_line_id", "=", inv_line.id),
                    ("account_id", "=", analytic_account.id),
                ]
            )

            if not existing_lines:
                # Create analytic line for this invoice line
                self.env["account.analytic.line"].create(
                    {
                        "name": inv_line.name or self.name,
                        "account_id": analytic_account.id,
                        "partner_id": inv_line.partner_id.id,
                        "unit_amount": inv_line.quantity,
                        "product_id": inv_line.product_id.id,
                        "product_uom_id": inv_line.product_uom_id.id,
                        "amount": -inv_line.balance,  # Negative because it's revenue
                        "general_account_id": inv_line.account_id.id,
                        "move_line_id": inv_line.id,
                        "company_id": inv_line.company_id.id,
                        "category": "invoice",
                    }
                )
