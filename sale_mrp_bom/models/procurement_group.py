# Copyright 2025 360ERP (<https://www.360erp.com>)
# License LGPL-3.0 or later (https://www.gnu.org/licenses/lgpl.html).

from odoo import api, models


class ProcurementGroup(models.Model):
    _inherit = "procurement.group"

    @api.model
    def run(self, procurements, raise_user_error=True):
        """
        Handle phantom BoM (kit) procurements linked to sale order lines.

        If a procurement is for a kit product associated with a sale order line,
        this method explodes the kit into its components and generates new
        procurements for those components. Original procurements that are not
        kits, or not linked to a sale order line with a phantom BoM, are passed through.

        :param procurements: A list of Procurement namedtuples
        :param raise_user_error: Whether to raise UserError on failure
        :return: Result of the original run method
        """
        # Collect unique sale_line_ids from procurements that have them
        sale_line_ids = list(
            set(
                p.values.get("sale_line_id")
                for p in procurements
                if p.values.get("sale_line_id")
            )
        )

        # Pre-fetch sale lines and create a mapping for quick access
        sale_lines = self.env["sale.order.line"].browse(sale_line_ids)
        sale_lines_map = {sl.id: sl for sl in sale_lines}

        procurements_without_kit = []
        for procurement in procurements:
            sale_line_id = procurement.values.get("sale_line_id")
            sale_line = sale_lines_map.get(sale_line_id)

            bom_kit = (
                sale_line.bom_id.filtered(
                    lambda bm, pr=procurement: bm.type == "phantom"
                    and (
                        # If BoM has product_id, match the procurement's product_id
                        (bm.product_id and bm.product_id == pr.product_id)
                        or
                        # Otherwise (if BoM has no product_id), match the template_id
                        (
                            not bm.product_id
                            and bm.product_tmpl_id == pr.product_id.product_tmpl_id
                        )
                    )
                )
                if sale_line
                else False
            )
            if bom_kit:
                order_qty = procurement.product_uom._compute_quantity(
                    procurement.product_qty, bom_kit.product_uom_id, round=False
                )
                qty_to_produce = order_qty / bom_kit.product_qty
                _dummy, bom_sub_lines = bom_kit.explode(
                    procurement.product_id,
                    qty_to_produce,
                    never_attribute_values=procurement.values.get(
                        "never_product_template_attribute_value_ids"
                    ),
                )
                for bom_line, bom_line_data in bom_sub_lines:
                    bom_line_uom = bom_line.product_uom_id
                    quant_uom = bom_line.product_id.uom_id
                    # recreate dict of values since each child has its own bom_line_id
                    values = dict(procurement.values, bom_line_id=bom_line.id)
                    component_qty, procurement_uom = (
                        bom_line_uom._adjust_uom_quantities(
                            bom_line_data["qty"], quant_uom
                        )
                    )
                    procurements_without_kit.append(
                        self.env["procurement.group"].Procurement(
                            bom_line.product_id,
                            component_qty,
                            procurement_uom,
                            procurement.location_id,
                            procurement.name,
                            procurement.origin,
                            procurement.company_id,
                            values,
                        )
                    )
            else:
                procurements_without_kit.append(procurement)
        return super().run(procurements_without_kit, raise_user_error=raise_user_error)
