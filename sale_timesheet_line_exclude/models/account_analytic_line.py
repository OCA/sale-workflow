# Copyright 2018-2019 Brainbean Apps
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).

from odoo import fields, models, api, _
from odoo.exceptions import ValidationError


class AccountAnalyticLine(models.Model):
    _inherit = 'account.analytic.line'

    exclude_from_sale_order = fields.Boolean(
        string='Exclude from Sale Order',
        help=(
            'Checking this would exclude this timesheet entry from Sale Order'
        ),
    )

    @api.onchange('task_id', 'employee_id')
    def _onchange_task_id_employee_id(self):
        """Override implementation in sale_timesheet to call
        _timesheet_get_sale_line() instead of resolving so_line in-place"""
        if self.project_id:  # timesheet only
            self.so_line = self._timesheet_get_sale_line()
            return
        return super()._onchange_task_id_employee_id()

    @api.onchange('exclude_from_sale_order')
    def _onchange_exclude_from_sale_order(self):
        if self.project_id:  # timesheet only
            self.so_line = self._timesheet_get_sale_line()

    @api.constrains('exclude_from_sale_order')
    def _constrains_exclude_from_sale_order(self):
        if self.filtered(
            lambda line: line.timesheet_invoice_id and
                line.so_line.product_id.invoice_policy == 'delivery'
        ):
            raise ValidationError(_(
                'You can not modify timesheets in a way that would affect'
                ' invoices since these timesheets were already invoiced.'
            ))

    @api.multi
    def _timesheet_get_sale_line(self):
        self.ensure_one()
        return self._timesheet_determine_sale_line(
            **self._timesheet_determine_sale_line_arguments()
        ) if not self.exclude_from_sale_order else False

    @api.model
    def _timesheet_should_evaluate_so_line(self, values, check):
        return check([field_name in values for field_name in [
            'task_id',
            'employee_id',
            'exclude_from_sale_order',
        ]])

    @api.multi
    def _timesheet_determine_sale_line_arguments(self, values=None):
        return {
            'task': (
                self.env['project.task'].sudo().browse(values['task_id'])
            ) if values and 'task_id' in values else self.task_id,
            'employee': (
                self.env['hr.employee'].sudo().browse(values['employee_id'])
            ) if values and 'employee_id' in values else self.employee_id,
        }

    @api.multi
    @api.depends('exclude_from_sale_order')
    def _compute_timesheet_invoice_type(self):
        result = super()._compute_timesheet_invoice_type()
        for timesheet in self.filtered('project_id'):
            # Since no-task entries are 'non_billable_project', check only
            # entries with tasks
            if timesheet.task_id and timesheet.exclude_from_sale_order:
                timesheet.timesheet_invoice_type = 'non_billable'
        return result

    @api.model
    def _timesheet_preprocess(self, values):
        values = super()._timesheet_preprocess(values)
        if self._timesheet_should_evaluate_so_line(values, all):
            so_line = self._timesheet_determine_sale_line(
                **self._timesheet_determine_sale_line_arguments(values)
            ) if not values.get('exclude_from_sale_order') else False
            values['so_line'] = so_line.id if so_line else False
        return values

    @api.multi
    def _timesheet_postprocess_values(self, values):
        result = super()._timesheet_postprocess_values(values)
        if self._timesheet_should_evaluate_so_line(values, any):
            for timesheet in self:
                so_line = timesheet._timesheet_get_sale_line()
                result[timesheet.id].update({
                    'so_line': so_line.id if so_line else False,
                })
        return result
