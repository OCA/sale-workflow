# -*- coding: utf-8 -*-
##############################################################################
#
#  licence AGPL version 3 or later
#  see licence in __openerp__.py or http://www.gnu.org/licenses/agpl-3.0.txt
#  Copyright (C) 2014 Akretion (http://www.akretion.com).
#  @author David BEAL <david.beal@akretion.com>
#          Sébastien Beau <sebastien.beau@akretion.com>
#
##############################################################################

from openerp import models, api, fields


class MrpProduction(models.Model):
    """ Purpose to generate manufacturing base on custom product raw material
    """
    _inherit = 'mrp.production'

    lot_id = fields.Many2one('stock.production.lot', 'Lot')

    @api.multi
    def _action_compute_lines(self, properties=None):
        """
        We passe the production.id in the context so you can easily get
        retrieve the production information during the process that generate
        the line of needed for the production order. For exemple, you can in
        the function bom_explod read the information of the production order
        to customise the needed.
        """
        res = []
        for production in self:
            self = self.with_context(production_id=production.id)
            res = super(MrpProduction, self)._action_compute_lines(
                properties=properties)
        return res

    @api.model
    def _make_production_consume_line(self, line):
        move_id = super(MrpProduction, self).\
            _make_production_consume_line(line)
        if line.lot_id:
            move = self.env['stock.move'].browse(move_id)
            move.write({'restrict_lot_id': line.lot_id.id})
        return move_id


class ProcurementOrder(models.Model):
    _inherit = 'procurement.order'

    def _prepare_mo_vals(self, cr, uid, procurement, context=None):
        res = super(ProcurementOrder, self)._prepare_mo_vals(
            cr, uid, procurement, context=context)
        res.update({
            'lot_id': procurement.lot_id.id,
            'name': procurement.lot_id.name,
            })
        return res


class MrpBom(models.Model):
    _inherit = 'mrp.bom'

    @api.model
    def _get_custom_lot_vals(self, vals, idx):
        return {
            'name': "%s-%03d" % (vals['name'], idx),
        }

    @api.model
    def _bom_explode(self, bom, product, factor, properties=None, level=0,
                     routing_id=False, previous_products=None,
                     master_bom=None):
        product_lines, workcenter_lines = super(MrpBom, self)._bom_explode(
            bom, product, factor,
            properties=properties, level=level,
            routing_id=routing_id, previous_products=previous_products,
            master_bom=master_bom)
        production_id = self._context.get('production_id')
        if production_id:
            production = self.env['mrp.production'].browse(production_id)
            if production.lot_id:
                product_obj = self.env['product.product']
                prodlot_obj = self.env['stock.production.lot']
                idx = 0
                for line in product_lines:
                    product = product_obj.browse(line['product_id'])
                    if product.auto_generate_prodlot:
                        idx += 1
                        vals = production.lot_id.copy_data()[0]
                        vals.update(self._get_custom_lot_vals(vals, idx))
                        prodlot = prodlot_obj.create(vals)
                        line['lot_id'] = prodlot.id
        return product_lines, workcenter_lines


class MrpProductionProductLine(models.Model):
    _inherit = 'mrp.production.product.line'

    lot_id = fields.Many2one('stock.production.lot', 'Lot')
