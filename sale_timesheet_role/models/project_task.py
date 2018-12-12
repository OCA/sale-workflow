# Copyright 2018 Brainbean Apps
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo import fields, models, api


class ProjectTask(models.Model):
    _inherit = 'project.task'

    billable_type = fields.Selection(
        selection_add=[
            ('employee_role_rate', 'At Employee/Role Rate')
        ],
    )

    @api.multi
    def _compute_sale_order_id(self):
        result = super()._compute_sale_order_id()

        for task in self:
            if task.exclude_from_sale_order:
                continue

            if task.billable_type == 'employee_role_rate':
                task.sale_order_id = task.project_id.sale_order_id

        return result

    @api.multi
    def _compute_billable_type(self):
        result = super()._compute_billable_type()

        for task in self:
            if task.exclude_from_sale_order:
                continue

            if task.project_id.billable_type == 'employee_role_rate':
                task.billable_type = task.project_id.billable_type

        return result
