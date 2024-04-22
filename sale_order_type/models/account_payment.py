from odoo import api, models


class AccountPayment(models.Model):
    _inherit = "account.payment"

    @api.depends("available_partner_bank_ids", "journal_id")
    def _compute_partner_bank_id(self):
        """
        If the selected account is in the available accounts then the change is not made.
        """
        partner_bank_by_pay = {}
        for payment in self:
            partner_bank_by_pay[payment.id] = payment.partner_bank_id
        res = super(AccountPayment, self)._compute_partner_bank_id()
        for payment in self:
            if (partner_bank_by_pay.get(payment.id, False) 
                and partner_bank_by_pay.get(payment.id) 
                in payment.available_partner_bank_ids):
                payment.partner_bank_id = partner_bank_by_pay.get(payment.id)
        return res
    