# -*- coding: utf-8 -*-
#  © 2014 ToDay Akretion
#  @author Mourad EL HADJ MIMOUNE <mourad.elhadj.mimoune@akretion.com>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).


from odoo import models


class ProcurementOrder(models.Model):
    _inherit = 'procurement.order'

    def _prepare_mo_vals(self, bom):
        res = super(ProcurementOrder, self)._prepare_mo_vals(bom)
        if self.lot_id:
            res.update({
                'lot_id': self.lot_id.id,
                'name': self.lot_id.name,
            })
        return res
