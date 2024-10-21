# Copyright 2023 Michael Tietz (MT Software) <mtietz@mt-software.de>
# License LGPL-3.0 or later (http://www.gnu.org/licenses/lgpl.html).
from odoo import models


class StockRule(models.Model):
    _inherit = "stock.rule"

    def _get_custom_move_fields(self):
        res = super()._get_custom_move_fields()
        res.append("used_for_sale_reservation")
        return res

    def _run_pull(self, procurements):
        if not self.env.context.get("sale_stock_prebook_stop_proc_run"):
            return super()._run_pull(procurements)
        actions_to_run = []
        for procurement, rule in procurements:
            if rule.picking_type_id.code == "outgoing":
                actions_to_run.append((procurement, rule))
        super()._run_pull(actions_to_run)
