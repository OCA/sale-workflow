# Copyright 2019 Camptocamp SA
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo import api, fields, models


class SaleOrder(models.Model):
    _inherit = 'sale.order'
    _name = 'sale.order'

    timesheet_limit_date = fields.Date(
        string='Timesheet Limit Date',
        help='Invoice will be created with timesheet prior and including'
        ' the date set',
    )

    @api.model
    def create(self, vals):
        rec = super().create(vals)
        if 'timesheet_limit_date' in vals:
            rec._update_delivered_quantity(vals['timesheet_limit_date'])
        return rec

    @api.multi
    def write(self, vals):
        res = super().write(vals)
        if 'timesheet_limit_date' in vals:
            self._update_delivered_quantity(vals['timesheet_limit_date'])
        return res

    def _update_delivered_quantity(self, limit_date):
        lines = (
            self.mapped('order_line')
            .with_context(
                timesheet_limit_date=limit_date,
                sale_analytic_force_recompute=True,
            )
            .sudo()
        )
        lines._analytic_compute_delivered_quantity()

    @api.multi
    def action_invoice_create(self, grouped=False, final=False):
        # and drop limit date from sale order
        res = super().action_invoice_create(grouped, final)
        orders_with_ts_limit = self.filtered(lambda o: o.timesheet_limit_date)
        orders_with_ts_limit.write({'timesheet_limit_date': False})
        return res

    @api.multi
    def _prepare_invoice(self):
        # set apropriate limit date to new created invoice
        res = super()._prepare_invoice()
        if self.timesheet_limit_date:
            res['timesheet_limit_date'] = self.timesheet_limit_date
        return res
