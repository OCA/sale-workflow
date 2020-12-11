# Copyright (C) 2020 - Today: GRAP (http://www.grap.coop)
# @author Quentin DUPONT (quentin.dupont@grap.coop)
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

from odoo import api, fields, models


class SaleAdvancePaymentInv(models.TransientModel):
    _inherit = 'sale.advance.payment.inv'

    @api.model
    def _default_product_id(self):
        product_id = self.env.user.company_id.down_payment_product_id
        if not product_id.id:
            return super(SaleAdvancePaymentInv, self)._default_product_id()
        else:
            action = self.env.ref(
                "sale."
                "action_view_sale_advance_payment_inv").read()[0]
            action['context'] = {'product_id': product_id.id}
            return product_id

    product_id = fields.Many2one(default=_default_product_id)
