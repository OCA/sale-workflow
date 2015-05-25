# -*- encoding: utf-8 -*-
##############################################################################
#
#    Sale Start End Dates module for Odoo
#    Copyright (C) 2014-2015 Akretion (http://www.akretion.com)
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

from openerp import models, fields, api, _
from openerp.exceptions import ValidationError


class SaleOrder(models.Model):
    _inherit = 'sale.order'

    default_start_date = fields.Date(string='Default Start Date')
    default_end_date = fields.Date(string='Default End Date')

    @api.one
    @api.constrains('default_start_date', 'default_end_date')
    def _check_default_start_end_dates(self):
        if (
                self.default_start_date and
                self.default_end_date and
                self.default_start_date > self.default_end_date):
            raise ValidationError(
                _("Default Start Date should be before or be the "
                    "same as Default End Date for sale order %s")
                % self.name)

    @api.onchange('default_start_date')
    def default_start_date_change(self):
        if (
                self.default_start_date and
                self.default_end_date and
                self.default_start_date > self.default_end_date):
            self.default_end_date = self.default_start_date

    @api.onchange('default_end_date')
    def default_end_date_change(self):
        if (
                self.default_start_date and
                self.default_end_date and
                self.default_start_date > self.default_end_date):
            self.default_start_date = self.default_end_date


class SaleOrderLine(models.Model):
    _inherit = 'sale.order.line'

    @api.one
    @api.depends('start_date', 'end_date')
    def _compute_number_of_days(self):
        if self.start_date and self.end_date:
            self.number_of_days = (
                fields.Date.from_string(self.end_date)
                - fields.Date.from_string(self.start_date)).days + 1
        else:
            self.number_of_days = 0

    start_date = fields.Date(
        string='Start Date', readonly=True,
        states={'draft': [('readonly', False)]})
    end_date = fields.Date(
        string='End Date', readonly=True,
        states={'draft': [('readonly', False)]})
    number_of_days = fields.Integer(
        compute='_compute_number_of_days', string='Number of Days',
        readonly=True)
    must_have_dates = fields.Boolean(
        string='Must Have Start and End Dates', readonly=True,
        states={'draft': [('readonly', False)]})

    @api.one
    @api.constrains('start_date', 'end_date')
    def _check_start_end_dates(self):
        if self.product_id and self.must_have_dates:
            if not self.end_date:
                raise ValidationError(
                    _("Missing End Date for sale order line with "
                        "Product '%s'.")
                    % (self.product_id.name))
            if not self.start_date:
                raise ValidationError(
                    _("Missing Start Date for sale order line with "
                        "Product '%s'.")
                    % (self.product_id.name))
            if self.start_date > self.end_date:
                raise ValidationError(
                    _("Start Date should be before or be the same as "
                        "End Date for sale order line with Product '%s'.")
                    % (self.product_id.name))

# TODO check must_have_dates on SO validation ? or in constraint ?

    @api.model
    def _prepare_order_line_invoice_line(self, line, account_id=False):
        res = super(SaleOrderLine, self)._prepare_order_line_invoice_line(
            line, account_id=account_id)
        if line.must_have_dates:
            res.update({
                'start_date': line.start_date,
                'end_date': line.end_date,
                })
        return res

# Disable this method, because I can't put both an on_change in the
# XML and an @api.onchange on the same fields :-(
# And I prefer to use @api.onchange on higher-level modules
#    @api.multi
#    def start_end_dates_change(self, start_date, end_date):
#        res = {}
#        if start_date and end_date:
#            if end_date < start_date:
#                # We could have put a raise here
#                # but a warning is fine because we have the constraint
#                res['warning'] = {
#                    'title': _('Warning:'),
#                    'message': _("Start Date should be before or be the "
#                                 "same as End Date."),
#                }
#        return res

    @api.onchange('end_date')
    def end_date_change(self):
        if (
                self.start_date and self.end_date and
                self.start_date > self.end_date):
            self.start_date = self.end_date

    @api.onchange('start_date')
    def start_date_change(self):
        if (
                self.start_date and self.end_date and
                self.start_date > self.end_date):
            self.end_date = self.start_date

    @api.multi
    def product_id_change(
            self, pricelist, product, qty=0,
            uom=False, qty_uos=0, uos=False, name='', partner_id=False,
            lang=False, update_tax=True, date_order=False, packaging=False,
            fiscal_position=False, flag=False):
        res = super(SaleOrderLine, self).product_id_change(
            pricelist, product, qty=qty, uom=uom,
            qty_uos=qty_uos, uos=uos, name=name, partner_id=partner_id,
            lang=lang, update_tax=update_tax, date_order=date_order,
            packaging=packaging, fiscal_position=fiscal_position,
            flag=flag)
        if not product:
            res['value'].update({
                'must_have_dates': False,
                'start_date': False,
                'end_date': False,
                })
        else:
            product_o = self.env['product.product'].browse(product)
            if product_o.must_have_dates:
                res['value']['must_have_dates'] = True
                if self.env.context.get('default_start_date'):
                    res['value']['start_date'] = self.env.context.get(
                        'default_start_date')
                if self.env.context.get('default_end_date'):
                    res['value']['end_date'] = self.env.context.get(
                        'default_end_date')
            else:
                res['value'].update({
                    'must_have_dates': False,
                    'start_date': False,
                    'end_date': False,
                    })
        return res
