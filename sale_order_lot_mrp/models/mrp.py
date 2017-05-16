# -*- coding: utf-8 -*-
#  © 2014 ToDay Akretion
#  @author David BEAL <david.beal@akretion.com>
#  @author Sébastien Beau <sebastien.beau@akretion.com>
#  @author Mourad EL HADJ MIMOUNE <mourad.elhadj.mimoune@akretion.com>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).


from odoo import api, fields, models


class MrpProduction(models.Model):
    """ Purpose to generate manufacturing base on custom product raw material
    """
    _inherit = 'mrp.production'

    lot_id = fields.Many2one(
        'stock.production.lot',
        'Lot',
        index=True)

    @api.multi
    def button_plan(self):
        """
        We passe the production.id in the context so you can easily
        retrieve the production information during the process that generate
        the line of needed for the production order. For exemple, in
        the method explode() of 'mrp.bom', you can read the information
        of the production order to customise the needed.
        """
        for production in self:
            production = production.with_context(production=production)
            super(MrpProduction, production).button_plan()

    def _generate_finished_moves(self):
        move = super(MrpProduction, self).\
            _generate_finished_moves()
        move.restrict_lot_id = self.lot_id.id
        return move

    @api.model
    def _get_custom_lot_vals(self, vals, idx):
        return {
            'name': "%s-%d" % (vals['name'], idx),
        }

    def _workorders_create(self, bom, bom_data):
        """
        :param bom: in case of recursive boms:
         we could create work orders for child BoMs
        """
        workorders = super(MrpProduction, self)._workorders_create(
            bom, bom_data)
        prodlot_obj = self.env['stock.production.lot']
        idx = 0
        for workorder in workorders:
            if workorder.product_id.tracking != 'none' and\
                    workorder.product_id.auto_generate_prodlot:
                workorder.final_lot_id = workorder.production_id.lot_id
            for mv_lot in workorder.active_move_lot_ids:
                if mv_lot.product_id.tracking != 'none' and\
                        mv_lot.product_id.auto_generate_prodlot and\
                        workorder.final_lot_id:
                    idx += 1
                    vals = workorder.final_lot_id.copy_data()[0]
                    vals.update(self._get_custom_lot_vals(vals, idx))
                    vals.update({'product_id': mv_lot.product_id.id})
                    prodlot = prodlot_obj.create(vals)
                    mv_lot.lot_id = prodlot
        return workorders
