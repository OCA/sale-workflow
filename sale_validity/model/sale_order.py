# -*- coding: utf-8 -*-
#
#
#    Copyright 2013 Camptocamp SA
#
#    This program is free software: you can redistribute it and/or modify
#    it under the terms of the GNU Affero General Public License as
#    published by the Free Software Foundation, either version 3 of the
#    License, or (at your option) any later version.
#
#    This program is distributed in the hope that it will be useful,
#    but WITHOUT ANY WARRANTY; without even the implied warranty of
#    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#    GNU Affero General Public License for more details.
#
#    You should have received a copy of the GNU Affero General Public License
#    along with this program.  If not, see <http://www.gnu.org/licenses/>.
#
#
from dateutil.relativedelta import relativedelta

from openerp import models, fields, api


class SaleOrder(models.Model):
    _inherit = 'sale.order'

    date_validity = fields.Date(
        string='Valid Until', readonly=True, copy=False,
        help="Define date until when quotation is valid",
        states={
            'draft': [('readonly', False)],
            'sent': [('readonly', True)],
        },
        track_visibility='onchange',
        default=lambda rec: rec._default_date_validity())

    @api.model
    def _default_date_validity(self):
        date_validity_str = False
        company_pool = self.env['res.company']
        company_id = company_pool._company_default_get('sale.order')
        company = company_pool.browse(company_id)
        if company.default_sale_order_validity_days:
            today_str = fields.Date.context_today(self)
            today = fields.Date.from_string(today_str)
            date_validity = today + relativedelta(
                days=company.default_sale_order_validity_days)
            date_validity_str = fields.Date.to_string(date_validity)
        return date_validity_str

    @api.onchange('date_order')
    def _onchange_date_order(self):
        company_pool = self.env['res.company']
        if self.date_order:
            company = self.company_id
            if not company:
                company_id = company_pool._company_default_get('sale.order')
                company = company_pool.browse(company_id)
            if company.default_sale_order_validity_days:
                date_order = fields.Datetime.from_string(self.date_order)
                date_validity = date_order + relativedelta(
                    days=company.default_sale_order_validity_days)
                self.date_validity = fields.Date.to_string(date_validity)
