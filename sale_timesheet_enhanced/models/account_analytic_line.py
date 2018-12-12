# Copyright 2018 Brainbean Apps
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo import fields, models, api, _
from odoo.exceptions import UserError, ValidationError


class AccountAnalyticLine(models.Model):
    _inherit = 'account.analytic.line'

    exclude_from_sale_order = fields.Boolean(
        string='Exclude from Sale Order',
        help=(
            'Checking this would exclude this timesheet entry from Sale Order'
        ),
    )

    @api.onchange('exclude_from_sale_order')
    def _onchange_task_id_employee_id(self):
        if self.project_id:
            if self.exclude_from_sale_order:
                self.so_line = False
            else:
                self.so_line = self._timesheet_get_sale_line()

    @api.multi
    def action_determine_sale_order_line(self):
        for line in self:
            if self.exclude_from_sale_order:
                line.write({
                    'so_line': False,
                })
            else:
                so_line = line._timesheet_get_sale_line()
                line.write({
                    'so_line': so_line.id if so_line else False,
                })

    @api.multi
    def _timesheet_get_sale_line(self):
        self.ensure_one()

        result = self._timesheet_determine_sale_line(
            self.task_id,
            self.employee_id
        )

        return result or False

    @api.multi
    @api.depends('exclude_from_sale_order')
    def _compute_timesheet_invoice_type(self):
        result = super()._compute_timesheet_invoice_type()

        for timesheet in self:
            # Skip non-timesheet entries
            if not timesheet.project_id:
                continue

            # Since no-task entries are 'non_billable_project', check only
            # entries with tasks
            if timesheet.task_id and timesheet.exclude_from_sale_order:
                timesheet.timesheet_invoice_type = 'non_billable'

        return result

    @api.multi
    def _timesheet_postprocess_values(self, values):
        result = super()._timesheet_postprocess_values(values)

        if 'exclude_from_sale_order' in values:
            result = self._timesheet_postprocess_so_line(
                values,
                result
            )

        return result

    @api.multi
    def _timesheet_postprocess_so_line(self, values, result):
        for timesheet in self:
            if timesheet.exclude_from_sale_order:
                result[timesheet.id].update({
                    'so_line': False,
                })
            else:
                so_line = timesheet._timesheet_get_sale_line()
                result[timesheet.id].update({
                    'so_line': so_line.id if so_line else False,
                })

        return result

    def _check_sale_line_in_project_map(self):
        # Since super method is not extendable, override it completely
        # with backwards compatibility
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
                'sale_line_employee_role_ids.sale_line_id'
            )
            | self.project_id.mapped(
                'sale_line_employee_ids.sale_line_id'
            )
            | self.task_id.sale_line_id
            | self.project_id.sale_line_id
        )

    @api.multi
    def write(self, values):
        self._ensure_timesheet_invoice_consistency(
            values,
            ['exclude_from_sale_order']
        )

        return super().write(values)

    @api.multi
    def _ensure_timesheet_invoice_consistency(self, values, fields):
        def is_invoiced(timesheet):
            return timesheet.timesheet_invoice_id and \
                timesheet.so_line.product_id.invoice_policy == 'delivery'
        if any([field in values for field in fields]) and \
                self.filtered(is_invoiced):
            raise UserError(_(
                'You can not modify timesheets in a way that would affect'
                ' invoices since these timesheets were already invoiced.'
            ))
