# -*- encoding: utf-8 -*-
##############################################################################
# For copyright and license notices, see __openerp__.py file in root directory
##############################################################################

from openerp import api, models


class StockPicking(models.Model):
    _inherit = "stock.picking"

    @api.model
    def create(self, values):
        origin = values.get('origin', False)
        if origin:
            sale_obj = self.env['sale.order']
            sale = sale_obj.search([('name', '=', origin)], limit=1)
            values.update({'invoice_state': sale.type_id.invoice_state})
        return super(StockPicking, self).create(values)

    @api.model
    def _create_invoice_from_picking(self, picking, vals):
        if picking and picking.sale_id:
            sale = picking.sale_id
            if sale.type_id and sale.type_id.journal_id:
                vals['journal_id'] = sale.type_id.journal_id.id
        return super(StockPicking, self)._create_invoice_from_picking(picking,
                                                                      vals)
