# Copyright 2018 ACSONE SA/NV
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo import api, fields, models
from odoo.exceptions import ValidationError


class SaleOrder(models.Model):
    _inherit = "sale.order"

    action_project_manual_allowed = fields.Boolean(
        compute="_compute_action_project_manual_allowed"
    )

    @api.depends(
        "state",
        "order_line.is_service",
        "order_line.product_id.service_tracking",
    )
    def _compute_action_project_manual_allowed(self):
        for rec in self:
            rec.action_project_manual_allowed = rec.state in ("draft", "sent") and any(
                [
                    line.is_service
                    and line.product_id.service_tracking
                    in ("task_global_project", "project_only", "task_in_project")
                    for line in rec.order_line
                ]
            )

    def _compute_show_project_and_task_button(self):
        res = super()._compute_show_project_and_task_button()

        is_project_manager = self.env.user.has_group("project.group_project_manager")
        self_manual_project = self.filtered(
            lambda order: order.action_project_manual_allowed
        )
        for order in self_manual_project:
            order.show_project_button = order.project_count
            order.show_task_button = order.show_project_button or order.tasks_count
            order.show_create_project_button = (
                is_project_manager and not order.project_count
            )
        return res

    def _compute_show_hours_recorded_button(self):
        res = super()._compute_show_hours_recorded_button()
        self_manual_project = self.filtered(
            lambda order: order.action_project_manual_allowed
        )
        for order in self_manual_project:
            order.show_hours_recorded_button = (
                order.timesheet_count or order.project_count
            )
        return res

    def action_project_manual(self):
        """Generate project/task manually without confirming the SO."""
        self.action_project_manual_allowed_check()
        self.order_line.sudo().with_company(self.company_id).with_context(
            skip_auto_confirm_so=True
        )._timesheet_service_generation()

    def action_project_manual_allowed_check(self):
        for rec in self:
            if not rec.action_project_manual_allowed:
                raise ValidationError(
                    self.env._(
                        "You can anticipate the project creation only for "
                        "draft quotations which contain service with timesheet "
                        "generation. (SO: %s)"
                    )
                    % rec.display_name
                )
