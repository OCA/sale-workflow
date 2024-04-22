# -*- coding: utf-8 -*-
from odoo import models, fields, api, _


class AccountPayment(models.Model):
    _inherit = 'account.payment'

    @api.depends('available_partner_bank_ids', 'journal_id')
    def _compute_partner_bank_id(self):
        #TODO: Se lo debe eliminar cuando el ticket sea solventado por Odoo https://github.com/OCA/sale-workflow/issues/3074
        '''Método que permite seleccionar cualquiera de las cuentas bancarias 
        disponibles para el pago siempre y cuando se encuentre dentro de las cuentas bancarias disponibles
        Caso contrario se comporta como el método original
        Se lo realiza tal que el módulo sale_order_type trae conflictos con el campo partner_bank_id
        '''
        partner_bank_by_pay = {}
        for payment in self:
                partner_bank_by_pay[payment.id] = payment.partner_bank_id
        res = super(AccountPayment, self)._compute_partner_bank_id()
        for payment in self:
            if partner_bank_by_pay.get(payment.id, False) and partner_bank_by_pay.get(payment.id) in payment.available_partner_bank_ids:
                payment.partner_bank_id = partner_bank_by_pay.get(payment.id)