# Copyright 2018-2019 Brainbean Apps
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).

from odoo import models, api, _
from odoo.exceptions import ValidationError


class AccountAnalyticLine(models.Model):
    _inherit = 'account.analytic.line'

    @api.constrains('so_line', 'project_id', 'task_id')
    def _check_sale_line_in_project_map(self):
        """Since super method is not extendable, override it completely
        with backwards compatibility"""
        for timesheet in self:
            if not timesheet.project_id or not timesheet.so_line:
                continue
            if timesheet.so_line not in timesheet._get_valid_so_line_ids():
                raise ValidationError(_(
                    'This timesheet line cannot be billed: there is no Sale'
                    ' Order Item defined on the task, nor on the project.'
                    ' Please define one to save your timesheet line.'
                ))

    @api.multi
    def _get_valid_so_line_ids(self):
        self.ensure_one()
        return (
            self.project_id.mapped(
                'sale_line_employee_ids.sale_line_id'
            )
            | self.task_id.sale_line_id
            | self.project_id.sale_line_id
        )
