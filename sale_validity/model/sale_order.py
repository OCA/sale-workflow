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

from openerp.osv import fields, orm
from openerp.tools import DEFAULT_SERVER_DATE_FORMAT
from datetime import datetime
from dateutil.relativedelta import relativedelta


class sale_order(orm.Model):
    _inherit = "sale.order"

    _columns = {
        'date_validity': fields.date(
            "Valid Until",
            help="Define date until when quotation is valid",
            readonly=True,
            states={
                'draft': [('readonly', False)],
                'sent': [('readonly', True)],
            },
            track_visibility='onchange'),
    }

    def _default_date_validity(self, cr, uid, context=None):
        date_validity_str = False
        company_id = self.pool['res.company']._company_default_get(
            cr, uid, 'sale.order', context=context)
        company = self.pool['res.company'].browse(
            cr, uid, company_id, context=context)
        if company.default_sale_order_validity_days:
            today_str = fields.date.context_today(
                self, cr, uid, context=context)
            today = datetime.strptime(today_str, DEFAULT_SERVER_DATE_FORMAT)
            date_validity = today + relativedelta(
                days=company.default_sale_order_validity_days)
            date_validity_str = date_validity.strftime(
                DEFAULT_SERVER_DATE_FORMAT)
        return date_validity_str

    _defaults = {
        'date_validity': _default_date_validity,
    }

    def date_order_change(
            self, cr, uid, ids, date_order, date_validity, company_id,
            context=None):
        res = {'value': {}}
        if date_order:
            if not company_id:
                company_id = self.pool['res.company']._company_default_get(
                    cr, uid, 'sale.order', context=context)
            company = self.pool['res.company'].browse(
                cr, uid, company_id, context=context)
            if company.default_sale_order_validity_days:
                date_order = datetime.strptime(
                    date_order, DEFAULT_SERVER_DATE_FORMAT)
                date_validity = date_order + relativedelta(
                    days=company.default_sale_order_validity_days)
                res['value']['date_validity'] = date_validity.strftime(
                    DEFAULT_SERVER_DATE_FORMAT)
        return res
