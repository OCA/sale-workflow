# Copyright 2019 Camptocamp SA
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo import api, fields, models


class SaleOrder(models.Model):
    _inherit = 'sale.order'

    timesheet_limit_date = fields.Date(
        string='Timesheet Limit Date',
        help='Invoice will be created with timesheet prior and including'
        ' the date set',
    )

    @api.multi
    @api.depends('timesheet_limit_date')
    def _compute_timesheet_ids(self):
        # this method copy of base method, it injects date in domain
        for order in self:
            if order.analytic_account_id:
                domain = [
                    ('so_line', 'in', order.order_line.ids),
                    ('amount', '<=', 0.0),
                    ('project_id', '!=', False),
                ]
                if order.timesheet_limit_date:
                    domain.append(
                        ('date', '<=', order.timesheet_limit_date)
                    )
                order.timesheet_ids = self.env[
                    'account.analytic.line'].search(domain)
            else:
                order.timesheet_ids = []
            order.timesheet_count = len(order.timesheet_ids)

    @api.multi
    def action_invoice_create(self, grouped=False, final=False):
        # and drop limit date from sale order
        res = super().action_invoice_create(grouped, final)
        orders_with_ts_limit = self.filtered(lambda o: o.timesheet_limit_date)
        orders_with_ts_limit.write({'timesheet_limit_date': False})
        return res

    @api.multi
    def _prepare_invoice(self):
        # set appropriate limit date to new created invoice
        res = super()._prepare_invoice()
        if self.timesheet_limit_date:
            res['timesheet_limit_date'] = self.timesheet_limit_date
        return res
