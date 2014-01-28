# -*- encoding: utf-8 -*-
##############################################################################
#
#    Sale Start End Dates module for OpenERP
#    Copyright (C) 2014 Akretion (http://www.akretion.com)
#    @author Alexis de Lattre <alexis.delattre@akretion.com>
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
##############################################################################

from openerp.osv import orm, fields
from openerp.tools.translate import _


class sale_order_line(orm.Model):
    _inherit = 'sale.order.line'

    _columns = {
        'start_date': fields.date(
            'Start Date',
            readonly=True, states={'draft': [('readonly', False)]}),
        'end_date': fields.date(
            'End Date',
            readonly=True, states={'draft': [('readonly', False)]}),
        'must_have_dates': fields.boolean(
            'Must Have Start and End Dates',
            readonly=True, states={'draft': [('readonly', False)]}),
        }

    def _check_start_end_dates(self, cr, uid, ids):
        for line in self.browse(cr, uid, ids):
            if line.start_date and not line.end_date:
                raise orm.except_orm(
                    _('Error:'),
                    _("Missing End Date for sale order line with "
                        "Description '%s'.")
                    % (line.name))
            if line.end_date and not line.start_date:
                raise orm.except_orm(
                    _('Error:'),
                    _("Missing Start Date for sale order line with "
                        "Description '%s'.")
                    % (line.name))
            if line.end_date and line.start_date and \
                    line.start_date > line.end_date:
                raise orm.except_orm(
                    _('Error:'),
                    _("Start Date should be before or be the same as "
                        "End Date for sale order line with Description '%s'.")
                    % (line.name))
        return True

# TODO check must_have_dates on SO validation ? or in constraint ?

    _constraints = [
        (_check_start_end_dates, "Error msg in raise",
            ['start_date', 'end_date', 'product_id']),
        ]

    def _prepare_order_line_invoice_line(
            self, cr, uid, line, account_id=False, context=None):
        res = super(sale_order_line, self)._prepare_order_line_invoice_line(
            cr, uid, line, account_id=account_id, context=context)
        if line.must_have_dates:
            res.update({
                'start_date': line.start_date,
                'end_date': line.end_date,
                })
        return res

    def start_end_dates_change(
            self, cr, uid, ids, start_date, end_date, product_id,
            product_uom_qty, context=None):
        '''This function is designed to be inherited'''
        res = {}
        if start_date and end_date:
            if end_date < start_date:
                # We could have put a raise here
                # but a warning is fine because we have the constraint
                res['warning'] = {
                    'title': _('Warning:'),
                    'message': _("Start Date should be before or be the "
                                 "same as End Date."),
                }
        return res

    def product_id_change(
            self, cr, uid, ids, pricelist, product, qty=0,
            uom=False, qty_uos=0, uos=False, name='', partner_id=False,
            lang=False, update_tax=True, date_order=False, packaging=False,
            fiscal_position=False, flag=False, context=None):
        res = super(sale_order_line, self).product_id_change(
            cr, uid, ids, pricelist, product, qty=qty, uom=uom,
            qty_uos=qty_uos, uos=uos, name=name, partner_id=partner_id,
            lang=lang, update_tax=update_tax, date_order=date_order,
            packaging=packaging, fiscal_position=fiscal_position,
            flag=flag, context=context)
        if not product:
            res['value'].update({
                'must_have_dates': False,
                'start_date': False,
                'end_date': False,
                })
        else:
            product_o = self.pool['product.product'].browse(
                cr, uid, product, context=context)
            if product_o.must_have_dates:
                res['value'].update({'must_have_dates': True})
            else:
                res['value'].update({
                    'must_have_dates': False,
                    'start_date': False,
                    'end_date': False,
                    })
        return res
