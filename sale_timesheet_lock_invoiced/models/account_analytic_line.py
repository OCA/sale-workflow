# Copyright 2018 ACSONE SA/NV
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo import api, models, _
from odoo.exceptions import ValidationError


class AccountAnalyticLine(models.Model):

    _inherit = 'account.analytic.line'

    @api.multi
    def write(self, values):
        self._check_locked_lines()
        return super(AccountAnalyticLine, self).write(values)

    @api.multi
    def unlink(self):
        self._check_locked_lines()
        return super(AccountAnalyticLine, self).unlink()

    @api.multi
    def _check_locked_lines(self):
        for rec in self:
            if rec.timesheet_invoice_id:
                raise ValidationError(_(
                    "You can't modify/delete a timesheet line if it has been "
                    "invoiced. (Invoice: %s, Line: '%s')"
                ) % (
                    rec.timesheet_invoice_id.number,
                    rec.name,
                ))
