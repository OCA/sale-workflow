# Copyright 2017 Denis Leemann, Camptocamp SA
# Copyright 2021 Iván Todorovich, Camptocamp SA
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

from odoo import models


class StockMove(models.Model):
    _inherit = "stock.move"

    def _get_new_picking_values(self):
        # Overload to set carrier_id from the manual delivery wizard
        # Note: sale_manual_delivery is expected to be a manual.delivery record
        res = super()._get_new_picking_values()
        manual_delivery = self.env.context.get("sale_manual_delivery")
        if manual_delivery:
            if manual_delivery.partner_id:
                res["partner_id"] = manual_delivery.partner_id.id
            if manual_delivery.carrier_id:
                res["carrier_id"] = manual_delivery.carrier_id.id
        return res

    def _search_picking_for_assignation(self):
        # Overload to filter carrier_id
        # Note: sale_manual_delivery is expected to be a manual.delivery record
        manual_delivery = self.env.context.get("sale_manual_delivery")
        if manual_delivery:
            # original domain used in super()
            domain = self._search_picking_for_assignation_domain()
            # Filter on carrier
            if manual_delivery.carrier_id:
                domain += [
                    ("carrier_id", "=", manual_delivery.carrier_id.id),
                ]
            return self.env["stock.picking"].search(domain, limit=1)
        else:
            return super()._search_picking_for_assignation()
