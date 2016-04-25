# -*- encoding: utf-8 -*-
##############################################################################
# For copyright and license notices, see __openerp__.py file in root directory
##############################################################################

from openerp import api, models


class StockPicking(models.Model):
    _inherit = "stock.picking"

    @api.model
    def _create_invoice_from_picking(self, picking, vals):
        if picking and picking.sale_id:
            sale = picking.sale_id
            if (vals.get('type', '') == 'out_invoice' and
                    sale.type_id.journal_id):
                vals['journal_id'] = sale.type_id.journal_id.id
            elif (vals.get('type', '') == 'out_refund' and
                    sale.type_id.refund_journal_id):
                vals['journal_id'] = sale.type_id.refund_journal_id.id
        return super(StockPicking, self)._create_invoice_from_picking(picking,
                                                                      vals)
