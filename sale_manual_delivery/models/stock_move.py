# Copyright 2017 Denis Leemann, Camptocamp SA
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

from odoo import models, fields, api


class StockMove(models.Model):
    _inherit = "stock.move"

    carrier_id = fields.Many2one("delivery.carrier", string="Delivery Method")

    def _get_new_picking_values(self):
        res = super(StockMove, self)._get_new_picking_values()
        if self.env.context.get('vals'):
            vals = self.env.context.get('vals')
            if vals.get('carrier_id'):
                res["carrier_id"] = vals.get('carrier_id')
        return res

    @api.multi
    def _assign_picking(self):
        # Redefine method to filter on date_expected (allows to group moves
        # from the same manual delivery in one delivery)
        if "manual_delivery" not in self.env.context:
            return super(StockMove, self)._assign_picking()
        Picking = self.env["stock.picking"]
        self.recompute()

        for move in self:
            domain = [
                ("group_id", "=", move.group_id.id),
                ("location_id", "=", move.location_id.id),
                ("location_dest_id", "=", move.location_dest_id.id),
                ("picking_type_id", "=", move.picking_type_id.id),
                ("printed", "=", False),
                ("min_date", "=", move.date_expected),
                ("max_date", "=", move.date_expected),
                ("carrier_id", "=", move.carrier_id.id),
                (
                    "state",
                    "in",
                    [
                        "draft",
                        "confirmed",
                        "waiting",
                        "partially_available",
                        "assigned",
                    ],
                ),
            ]
            picking = Picking.search(domain, limit=1)
            if not picking.sale_id.manual_delivery:
                picking = Picking.create(move._get_new_picking_values())
            move.write({"picking_id": picking.id})
        return True
