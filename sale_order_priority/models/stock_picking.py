from odoo import models


class Picking(models.Model):
    _inherit = "stock.picking"

    def action_assign(self):
        res = super(Picking, self).action_assign()
        picking_priority = self.env.context.get("sale_priority")
        self.priority = picking_priority if picking_priority else 0
        return res
