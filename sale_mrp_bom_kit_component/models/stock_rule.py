# Copyright 2026 Eshan Desle
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).

from odoo import api, models


class StockRule(models.Model):
    _inherit = "stock.rule"

    @api.model
    def run(self, procurements, raise_user_error=True):
        """
        Handle kit procurements with customized kit components.
        For sale order lines with kit_component_ids, only procurements for
        selected components (is_selected=True) are generated.
        """
        sale_line_ids = list(
            {
                p.values.get("sale_line_id")
                for p in procurements
                if p.values.get("sale_line_id")
            }
        )
        sale_lines = self.env["sale.order.line"].browse(sale_line_ids)
        sale_lines_map = {sl.id: sl for sl in sale_lines}

        new_procurements = []
        for procurement in procurements:
            sale_line_id = procurement.values.get("sale_line_id")
            sale_line = sale_lines_map.get(sale_line_id)

            if (
                sale_line
                and sale_line.is_kit
                and sale_line.kit_component_ids
                and procurement.product_id == sale_line.product_id
            ):
                bom_kit = sale_line._get_kit_bom()
                if bom_kit:
                    order_qty = procurement.product_uom._compute_quantity(
                        procurement.product_qty, bom_kit.product_uom_id, round=False
                    )
                    qty_factor = order_qty / (bom_kit.product_qty or 1.0)
                    selected_comps = sale_line.kit_component_ids.filtered("is_selected")
                    for comp in selected_comps:
                        comp_uom = comp.product_uom_id
                        quant_uom = comp.product_id.uom_id
                        total_comp_qty = comp.product_qty * qty_factor
                        component_qty, procurement_uom = (
                            comp_uom._adjust_uom_quantities(total_comp_qty, quant_uom)
                        )
                        values = dict(
                            procurement.values,
                            bom_line_id=comp.bom_line_id.id
                            if comp.bom_line_id
                            else False,
                        )
                        new_procurements.append(
                            self.env["stock.rule"].Procurement(
                                comp.product_id,
                                component_qty,
                                procurement_uom,
                                procurement.location_id,
                                procurement.name,
                                procurement.origin,
                                procurement.company_id,
                                values,
                            )
                        )
                    continue

            new_procurements.append(procurement)

        return super().run(new_procurements, raise_user_error=raise_user_error)
