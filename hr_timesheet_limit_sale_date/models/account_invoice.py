# Copyright 2019 Camptocamp SA
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo import api, fields, models
from odoo.osv import expression


class AccountInvoice(models.Model):
    _inherit = 'account.invoice'

    timesheet_limit_date = fields.Date(string='Timesheet Limit Date')

    @api.multi
    def _get_compute_timesheet_revenue_domain(self, so_line_ids):
        # force invoice date instead of order date
        domain = super()._get_compute_timesheet_revenue_domain(so_line_ids)
        expr = ('date', '<=', self.timesheet_limit_date)
        for i, rec in enumerate(domain):
            if 'date' in rec:
                domain[i] = expr
                break
        else:
            domain = expression.AND([domain, [expr]])
        return domain
