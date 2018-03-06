# -*- coding: utf-8 -*-
# Copyright (C) 2016  Akretion
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from openerp import fields, models, api
from openerp.tools import DEFAULT_SERVER_DATETIME_FORMAT
from datetime import datetime, timedelta


class SaleOrder(models.Model):
    _inherit = 'sale.order'

    datetime_confirm = fields.Datetime(string='Confirmation Date', copy=False)

    @api.multi
    def action_confirm(self):
        datetime_confirm = fields.Datetime.now()
        self.write({'datetime_confirm': datetime_confirm})
        return super(SaleOrder, self).action_confirm()


class SaleOrderLine(models.Model):
    _inherit = 'sale.order.line'

    @api.multi
    def _prepare_order_line_procurement(self, group_id=False):
        vals = super(SaleOrderLine, self)._prepare_order_line_procurement(
            group_id=group_id)
        datetime_confirm = datetime.strptime(self.order_id.datetime_confirm,
                                             DEFAULT_SERVER_DATETIME_FORMAT)
        date_planned = datetime_confirm + timedelta(
            days=self.customer_lead or 0.0) - \
            timedelta(days=self.order_id.company_id.security_lead)
        vals.update({
            'date_planned': date_planned.strftime(
                DEFAULT_SERVER_DATETIME_FORMAT),
        })
        return vals
