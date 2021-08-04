# Copyright 2018 ACSONE SA/NV
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo import api, fields, models, _
from odoo.exceptions import ValidationError


class SaleOrder(models.Model):

    _inherit = 'sale.order'

    action_project_manual_allowed = fields.Boolean(
        compute='_compute_action_project_manual_allowed'
    )

    @api.multi
    @api.depends(
        'state',
        'order_line.is_service',
        'order_line.product_id.service_tracking',
    )
    def _compute_action_project_manual_allowed(self):
        for rec in self:
            rec.action_project_manual_allowed = (
                rec.state in ('draft', 'sent') and
                any([
                    line.is_service and
                    line.product_id.service_tracking in (
                        'task_global_project',
                        'project_only',
                        'task_new_project'
                    )
                    for line in rec.order_line
                ])
            )

    @api.multi
    def action_project_manual(self):
        self.action_project_manual_allowed_check()
        self.order_line._timesheet_service_generation()

    @api.multi
    def action_project_manual_allowed_check(self):
        for rec in self:
            if not rec.action_project_manual_allowed:
                raise ValidationError(_(
                    "You can anticipate the project creation only for "
                    "draft quotations which contain service with timesheet "
                    "generation. (SO: %s)"
                ) % rec.display_name)
