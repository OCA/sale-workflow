# -*- coding: utf-8 -*-
# © initOS GmbH 2016
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from openerp import models, api


class SaleOrder(models.Model):
    _inherit = 'sale.order'

    @api.multi
    def automatic_payment(self, amount=None):
        """ Add some limitations to the creation of automatic_payments.
        """
        self.ensure_one()
        # do nothing when it isn't allow
        if self.payment_method_id and \
           self.payment_method_id.allow_automatic_payment == 'never':
            return True
        return super(SaleOrder, self).automatic_payment(amount=amount)
