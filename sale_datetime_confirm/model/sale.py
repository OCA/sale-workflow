# -*- coding: utf-8 -*-
#########################################################################
#  Copyright (C) 2016  Akretion                                         #
#                                                                       #
# This program is free software: you can redistribute it and/or modify  #
# it under the terms of the GNU Affero General Public License as        #
# published by the Free Software Foundation, either version 3 of the    #
# License, or (at your option) any later version.                       #
#                                                                       #
# This program is distributed in the hope that it will be useful,       #
# but WITHOUT ANY WARRANTY; without even the implied warranty of        #
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the         #
# GNU Affero General Public Licensefor more details.                    #
#                                                                       #
# You should have received a copy of the                                #
# GNU Affero General Public License                                     #
# along with this program.  If not, see <http://www.gnu.org/licenses/>. #
#                                                                       #
#########################################################################

from openerp import fields, models, api
from openerp.tools import DEFAULT_SERVER_DATETIME_FORMAT
from datetime import datetime, timedelta


class SaleOrder(models.Model):
    _inherit = 'sale.order'

    datetime_confirm = fields.Datetime(string='Confirm Date', copy=False)

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
