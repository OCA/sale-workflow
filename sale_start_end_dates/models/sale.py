# -*- coding: utf-8 -*-
# Copyright 2014-2016 Akretion (http://www.akretion.com)
# @author Alexis de Lattre <alexis.delattre@akretion.com>
# Copyright 2016 Sodexis (http://sodexis.com)
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo import models, fields, api, _
from odoo.exceptions import ValidationError
from dateutil.relativedelta import relativedelta


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

    start_date = fields.Date(
        string='Start Date', readonly=True,
        states={'draft': [('readonly', False)]})
    end_date = fields.Date(
        string='End Date', readonly=True,
        states={'draft': [('readonly', False)]})
    number_of_days = fields.Integer(string='Number of Days')
    must_have_dates = fields.Boolean(
        related='product_id.must_have_dates', readonly=True)

    @api.one
    @api.constrains('start_date', 'end_date', 'number_of_days')
    def _check_start_end_dates(self):
        if self.product_id and self.must_have_dates:
            if not self.end_date:
                raise ValidationError(_(
                    "Missing End Date for sale order line with "
                    "Product '%s'.") % (self.product_id.name))
            if not self.start_date:
                raise ValidationError(_(
                    "Missing Start Date for sale order line with "
                    "Product '%s'.") % (self.product_id.name))
            if not self.number_of_days:
                raise ValidationError(_(
                    "Missing number of days for sale order line with "
                    "Product '%s'.") % (self.product_id.name))
            if self.start_date > self.end_date:
                raise ValidationError(_(
                    "Start Date should be before or be the same as "
                    "End Date for sale order line with Product '%s'.")
                    % (self.product_id.name))
            if self.number_of_days < 0:
                raise ValidationError(_(
                    "On sale order line with Product '%s', the "
                    "number of days is negative ; this is not allowed.")
                    % (self.product_id.name))
            days_delta = (
                fields.Date.from_string(self.end_date) -
                fields.Date.from_string(self.start_date)).days + 1
            if self.number_of_days != days_delta:
                raise ValidationError(_(
                    "On the sale order line with Product '%s', "
                    "there are %d days between the Start Date (%s) and "
                    "the End Date (%s), but the number of days field "
                    "has a value of %d days.")
                    % (self.product_id.name, days_delta, self.start_date,
                        self.end_date, self.number_of_days))

    @api.multi
    def _prepare_invoice_line(self, qty):
        self.ensure_one()
        res = super(SaleOrderLine, self)._prepare_invoice_line(qty)
        if self.must_have_dates:
            res.update({
                'start_date': self.start_date,
                'end_date': self.end_date,
                })
        return res

    @api.onchange('end_date')
    def end_date_change(self):
        if self.end_date:
            if self.start_date and self.start_date > self.end_date:
                self.start_date = self.end_date
            if self.start_date:
                number_of_days = (
                    fields.Date.from_string(self.end_date) -
                    fields.Date.from_string(self.start_date)).days + 1
                if self.number_of_days != number_of_days:
                    self.number_of_days = number_of_days

    @api.onchange('start_date')
    def start_date_change(self):
        if self.start_date:
            if self.end_date and self.start_date > self.end_date:
                self.end_date = self.start_date
            if self.end_date:
                number_of_days = (
                    fields.Date.from_string(self.end_date) -
                    fields.Date.from_string(self.start_date)).days + 1
                if self.number_of_days != number_of_days:
                    self.number_of_days = number_of_days

    @api.onchange('number_of_days')
    def number_of_days_change(self):
        if self.number_of_days:
            if self.start_date:
                end_date_dt = fields.Date.from_string(self.start_date) +\
                    relativedelta(days=self.number_of_days - 1)
                end_date = fields.Date.to_string(end_date_dt)
                if self.end_date != end_date:
                    self.end_date = end_date
            elif self.end_date:
                self.start_date = fields.Date.from_string(self.end_date) -\
                    relativedelta(days=self.number_of_days - 1)

    @api.onchange('product_id')
    def start_end_dates_product_id_change(self):
        if self.product_id:
            if self.order_id.default_start_date:
                self.start_date = self.order_id.default_start_date
            else:
                self.start_date = False
            if self.order_id.default_end_date:
                self.end_date = self.order_id.default_end_date
            else:
                self.end_date = False
        else:
            self.start_date = False
            self.end_date = False
