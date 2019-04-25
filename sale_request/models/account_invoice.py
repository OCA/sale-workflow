# Copyright 2019 JARSA Sistemas S.A. de C.V.
# License LGPL-3.0 or later (https://www.gnu.org/licenses/lgpl.html).

from odoo import _, api, models
from odoo.exceptions import UserError


class AccountInvoiceLine(models.Model):
    _inherit = 'account.invoice.line'

    @api.multi
    def write(self, values):
        name_user = self.env.user.name
        fields_blocked = ['quantity', 'price_unit', 'invoice_line_tax_ids']
        if self.user_has_groups('account.group_account_invoice'):
            for rec in fields_blocked:
                if rec in values:
                    raise UserError(
                        _('The user %s can not permission to edit the price'
                            'unit, quantity and taxes') % name_user)
        return super().write(values)
