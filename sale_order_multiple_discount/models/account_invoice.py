# Copyright 2018 Onestein (<http://www.onestein.eu>)
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

from odoo import fields, models, api, _
from odoo.exceptions import ValidationError, Warning
import re


class AccountInvoiceLine(models.Model):
    _inherit = "account.invoice.line"

    multiple_discount = fields.Char('Discount (%)')

    @api.model
    def _validate_discount(self, discount):
        discount_regex = re.compile(
            r'^(\s*[-+]{0,1}\s*\d+([,.]\d+)?){1}'
            r'(\s*[-+]\s*\d+([,.]\d+)?\s*)*$'
        )

        # This regex is composed of 2 parts:
        # 1) A starting number which is mandatory {1} composed of:
        #    a) \s* = any number of starting spaces
        #    b) [-+]{0,1} = an optional symbol '+' or '-'
        #    c) \s* = any number of spaces
        #    d) \d+ = a digit sequence of length at least 1
        #    e) ([,.]\d+)? = an optional decimal part, composed of a '.' or ','
        #       symbol followed by a digital sequence of length at least 1
        # 2) An optional list of other numbers each one composed of:
        #    a) \s* = any number of starting spaces
        #    b) [-+] = a mandatory '+' or '-' symbol
        #    c) \s* = any number of spaces
        #    d) \d+ = a digit sequence of length at least 1
        #    e) ([,.]\d+)? = an optional decimal part, composed of a '.' or ','
        #       symbol followed by a digital sequence of length at least 1
        #    f) \s* = any number of ending spaces

        if discount and not discount_regex.match(discount):
            return False
        return True

    @api.onchange('multiple_discount')
    def onchange_multiple_discount(self):
        def _normalize_discount(discount):
            discount = discount.replace(" ", "")
            discount = discount.replace(",", ".")
            if discount and discount[0] == '+':
                discount = discount[1:]
            return discount

        for line in self:
            if line.multiple_discount:
                if self._validate_discount(line.multiple_discount):
                    normalized_discount = _normalize_discount(
                        line.multiple_discount)
                else:
                    line.discount = 0
                    raise Warning(
                        _('Warning! The discount format is not recognized.'))

                tokens = re.split(r'([+-])', normalized_discount)
                numeric_tokens = []
                last_sign = 1
                for token in tokens:
                    if token == '-':
                        last_sign = -1
                    elif token == '+':
                        last_sign = 1
                    else:
                        numeric_tokens.append(float(token)*last_sign)
                marginal_discount = 1
                for token in numeric_tokens:
                    marginal_discount = marginal_discount * (1-(token/100))
                total_discount = 1 - marginal_discount
                line.discount = total_discount * 100

                if normalized_discount != line.multiple_discount:
                    line.multiple_discount = normalized_discount

            else:
                line.discount = 0

    @api.constrains('multiple_discount')
    def validate_discount(self):
        for line in self:
            if line.multiple_discount and not self._validate_discount(
                    line.multiple_discount):
                raise ValidationError(
                    _('Warning! The discount format is not recognized.'))

    @api.multi
    def write(self, vals):
        res = super(AccountInvoiceLine, self).write(vals)
        if 'multiple_discount' in vals:
            for line in self:
                line.onchange_multiple_discount()
        return res
