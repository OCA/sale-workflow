# Copyright 2018 Brainbean Apps
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo import models, api


class AccountAnalyticLine(models.Model):
    _inherit = 'account.analytic.line'

    @api.multi
    def _timesheet_get_sale_line(self):
        self.ensure_one()

        if self.task_id.billable_type == 'employee_role_rate':
            Map = self.env['project.employee.role.sale.order.line.map']
            mapping = Map.search([
                ('project_id', '=', self.project_id.id),
                ('employee_id', '=', self.employee_id.id),
                ('role_id', '=', self.role_id.id),
            ])
            if not mapping:
                mapping = Map.search([
                    ('project_id', '=', self.project_id.id),
                    ('employee_id', '=', self.employee_id.id),
                    ('role_id', '=', False),
                ])
            if not mapping:
                mapping = Map.search([
                    ('project_id', '=', self.project_id.id),
                    ('employee_id', '=', False),
                    ('role_id', '=', self.role_id.id),
                ])
            if not mapping:
                return self.env['sale.order.line']
            return mapping.sale_line_id

        return super()._timesheet_get_sale_line()

    @api.onchange('role_id')
    def _onchange_task_id_employee_id(self):
        # NOTE: _timesheet_get_sale_line is called by super
        return super()._onchange_task_id_employee_id()

    def _get_valid_so_line_ids(self):
        return (
            super()._get_valid_so_line_ids()
            | self.project_id.mapped(
                'sale_line_employee_role_ids.sale_line_id'
            )
        )

    @api.multi
    def _timesheet_postprocess_values(self, values):
        result = super()._timesheet_postprocess_values(values)

        if 'role_id' in values:
            result = self._timesheet_postprocess_so_line(
                values,
                result
            )

        return result

    @api.multi
    def write(self, values):
        self._ensure_timesheet_invoice_consistency(
            values,
            ['role_id']
        )

        return super().write(values)
