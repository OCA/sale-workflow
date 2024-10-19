from odoo import api, models


class AccountPayment(models.Model):
    _inherit = "account.payment"

    @api.depends("journal_id")
    def _compute_currency_id(self):
        for rec in self:
            currency = rec.currency_id
            res = super()._compute_currency_id()
            if currency and currency != rec.journal_id.company_id.currency_id:
                rec.currency_id = currency
        return res
