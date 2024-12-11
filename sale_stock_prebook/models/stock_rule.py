# Copyright 2023 Michael Tietz (MT Software) <mtietz@mt-software.de>
# License LGPL-3.0 or later (http://www.gnu.org/licenses/lgpl.html).
from odoo import fields, models


class StockRule(models.Model):
    _inherit = "stock.rule"

    prebook_picking_type_id = fields.Many2one(
        "stock.picking.type",
        "Operation Type for Prebooking",
        required=False,
        check_company=True,
        domain="[('code', '=?', picking_type_code_domain)]",
        help="This operation type will be used for prebooking stock for sale orders. "
        "It's therefore only relevant for rules that are used for sale order lines.",
    )

    def _get_stock_move_values(
        self,
        product_id,
        product_qty,
        product_uom,
        location_dest_id,
        name,
        origin,
        company_id,
        values,
    ):
        res = super()._get_stock_move_values(
            product_id,
            product_qty,
            product_uom,
            location_dest_id,
            name,
            origin,
            company_id,
            values,
        )
        if values.get("used_for_sale_reservation") and self.prebook_picking_type_id:
            res["picking_type_id"] = self.prebook_picking_type_id.id
        return res

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
