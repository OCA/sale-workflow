# Copyright 2019 Camptocamp SA
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).
from odoo import _, api, exceptions, models
from odoo.osv import expression


class SaleOrderLine(models.Model):
    _inherit = 'sale.order.line'
    _name = 'sale.order.line'

    @api.multi
    def _analytic_compute_delivered_quantity_domain(self):
        domain = super()._analytic_compute_delivered_quantity_domain()

        timesheet_limit_date = self.env.context.get('timesheet_limit_date')
        if timesheet_limit_date is None:
            return domain
        # if multiple sale order selected do not pass
        if len(self.mapped('order_id')) > 1:
            raise exceptions.UserError(
                _('You cannot apply the TS limit date on multiple orders.')
            )
        if timesheet_limit_date:
            domain = expression.AND(
                [domain, [('date', '<=', timesheet_limit_date)]]
            )
        return domain
