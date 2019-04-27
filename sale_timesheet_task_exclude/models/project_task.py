# Copyright 2019 Brainbean Apps (https://brainbeanapps.com)
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).

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
        for task in self.filtered('exclude_from_sale_order'):
            task.billable_type = 'no'

    @api.multi
    def write(self, vals):
        res = super().write(vals)
        if 'exclude_from_sale_order' in vals:
            # If tasks changed their exclude_from_sale_order, update all AALs
            # that have not been invoiced yet
            for timesheet in self.timesheet_ids.filtered(
                lambda line: not line.timesheet_invoice_id
            ):
                timesheet._onchange_task_id_employee_id()
        return res
