# Copyright 2019 David BEAL @ Akretion
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

from odoo import _, api, models
from odoo.exceptions import UserError


class SaleOrder(models.Model):
    _inherit = 'sale.order'

    @api.multi
    def recompute_prices(self):
        for sale in self.filtered(lambda s: s.invoice_status != 'invoiced'):
            before = sale.amount_untaxed
            for sol in sale.order_line:
                try:
                    sol.product_id_change()
                    sol._compute_amount()
                except UserError as e:
                    raise UserError(e)
                except Exception as e:
                    raise Exception(e)
            if sale.amount_untaxed != before:
                message = _("Untaxed amount recomputed from %s to %s" % (
                    before, sale.amount_untaxed))
                sale.message_post(body=message)
