# -*- encoding: utf-8 -*-
##############################################################################
# For copyright and license notices, see __openerp__.py file in root directory
##############################################################################
from openerp import models, api


class sale_order(models.Model):
    _inherit = 'sale.order'

    @api.model
    def create(self, vals):
        result = super(sale_order, self).create(vals)
        result.expand_packs()
        return result

    @api.multi
    def write(self, vals):
        result = super(sale_order, self).write(vals)
        if vals.get('order_line'):
            self.expand_packs()
        return result

    # def copy(self, cr, uid, id, default={}, context=None):
    #     line_obj = self.pool.get('sale.order.line')
    #     result = super(sale_order, self).copy(cr, uid, id, default, context)
    #     sale = self.browse(cr, uid, result, context)
    #     for line in sale.order_line:
    #         if line.pack_parent_line_id:
    #             line_obj.unlink(cr, uid, [line.id], context)
    #     self.expand_packs(cr, uid, sale.id, context)
    #     return result

    @api.one
    def expand_packs(self):
        """
        """
        pack_lines = self.order_line.filtered(
                lambda l: l.state == 'draft' and
                l.product_id.pack and
                not l.product_id.sale_order_pack)
        print 'pack_lines', pack_lines
        while pack_lines:
            pack_lines = pack_lines.update_pack_lines()

# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:
