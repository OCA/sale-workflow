from odoo import models


class Picking(models.Model):
    _inherit = "stock.picking"

    def action_confirm(self):
        res = super().action_confirm()
        picking_priority = self.env.context.get("sale_priority", False)
        self.write({"priority": picking_priority or 0})
        return res
