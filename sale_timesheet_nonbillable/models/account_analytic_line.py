# Copyright 2018 Brainbean Apps (https://brainbeanapps.com)
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo import fields, models, api, _
from odoo.exceptions import UserError


class AccountAnalyticLine(models.Model):
    _inherit = 'account.analytic.line'

    timesheet_exclude_from_billing = fields.Boolean(
        string='Exclude From Billing',
        help=(
            'Checking this would exclude this timesheet entry from sale order'
            ' regardless of the billing setting of the task.'
        ),
    )

    @api.multi
    @api.depends(
        'so_line.product_id',
        'project_id',
        'task_id',
        'timesheet_exclude_from_billing',
    )
    def _compute_timesheet_invoice_type(self):
        result = super()._compute_timesheet_invoice_type()

        for timesheet in self:
            # Skip non-timesheet entries
            if not timesheet.project_id:
                continue

            # Since no-task entries are 'non_billable_project', check only
            # entries with tasks
            if timesheet.task_id and timesheet.timesheet_exclude_from_billing:
                timesheet.timesheet_invoice_type = 'non_billable'

        return result

    @api.onchange(
        'employee_id',
        'timesheet_exclude_from_billing',
    )
    def _onchange_task_id_employee_id(self):
        result = super()._onchange_task_id_employee_id()

        if self.project_id and self.task_id \
                and self.timesheet_exclude_from_billing:
            self.so_line = False

        return result

    @api.multi
    def write(self, values):
        # Extend prevention to update invoiced if one line is of type delivery
        def is_invoiced(timesheet):
            return timesheet.timesheet_invoice_id and \
                timesheet.so_line.product_id.invoice_policy == 'delivery'
        if 'timesheet_exclude_from_billing' in values and \
                self.filtered(is_invoiced):
            raise UserError(_(
                'You can not modify timesheets in a way that would affect'
                ' invoices since these timesheets were already invoiced.'
            ))

        return super().write(values)

    @api.multi
    def _timesheet_postprocess_values(self, values):
        result = super()._timesheet_postprocess_values(values)

        if 'timesheet_exclude_from_billing' in values:
            for timesheet in self:
                result[timesheet.id].update({
                    'so_line': timesheet._timesheet_determine_sale_line(
                        timesheet.task_id,
                        timesheet.employee_id
                    ).id,
                })

        return result

    @api.model
    def _timesheet_determine_sale_line(self, task, employee):
        result = super()._timesheet_determine_sale_line(task, employee)

        if task and self.timesheet_exclude_from_billing:
            return self.env['sale.order.line']

        return result
