# Copyright Copyright 2021 Daniel Dominguez, Manuel Calero - https://xtendoo.es
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).
from odoo import models


class SaleOrder(models.Model):
    _inherit = "sale.order"

    def action_view_picking(self):
        pick_ids = self.mapped("picking_ids").sorted("id")
        action = self.env.ref("stock.action_picking_tree_all")
        result = action.read()[0]
        # override the context to get id of the default filtering on operation type
        result["context"] = {
            "default_partner_id": self.partner_id.id,
            "default_origin": self.name,
        }
        result["domain"] = [("id", "in", pick_ids.ids)]
        result["res_id"] = pick_ids[:1].id
        # choose the view_mode accordingly
        res = self.env.ref("stock.view_picking_form", False)
        form_view = [(res and res.id or False, "form")]
        if "views" in result:
            result["views"] = form_view + [
                (state, view) for state, view in result["views"] if view != "form"
            ]
        else:
            result["views"] = form_view
        return result
