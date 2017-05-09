# -*- coding: utf-8 -*-
# Copyright 2017 Camptocamp SA
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html)

from odoo import _, api, exceptions, models
from odoo.tools import float_is_zero


class AccountInvoice(models.Model):
    _inherit = 'account.invoice'

    @api.multi
    def order_lines_layouted(self):
        original_pages = super(AccountInvoice, self).order_lines_layouted()
        pages = []
        for page in original_pages:
            new_page = []
            for section in page:
                # lines are grouped by layout_category_id so look
                # only the first one
                if section['lines'][0].layout_category_id.hidden:
                    continue
                new_page.append(section)
            if new_page:
                pages.append(new_page)
        return pages


class AccountInvoiceLine(models.Model):
    _inherit = 'account.invoice.line'

    @api.constrains('layout_category_id', 'price_unit')
    def _check_hidden_layout_category_price_unit(self):
        for line in self:
            if not line.layout_category_id.hidden:
                continue
            rounding = line.invoice_id.currency_id.rounding
            if not float_is_zero(line.price_unit, precision_rounding=rounding):
                raise exceptions.ValidationError(
                    _('Lines in hidden sections cannot have prices.')
                )
