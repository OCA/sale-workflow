# Copyright 2018 Brainbean Apps
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo import fields, models, api


class ProjectTask(models.Model):
    _inherit = 'project.task'

    exclude_from_sale_order = fields.Boolean(
        string='Exclude from Sale Order',
        help=(
            'Checking this would exclude any timesheet entries logged towards'
            ' this task from Sale Order'
        ),
    )

    @api.multi
    @api.depends('exclude_from_sale_order')
    def _compute_billable_type(self):
        super()._compute_billable_type()

        for task in self:
            if task.exclude_from_sale_order:
                task.billable_type = 'no'
