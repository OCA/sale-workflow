# Copyright 2020-22 ForgeFlow S.L.
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl.html).

from odoo import api, models


class ProcurementGroup(models.Model):
    _inherit = "procurement.group"

    @api.model
    def run(self, procurements, raise_user_error=True):
        new_procs = []
        Proc = self.env["procurement.group"].Procurement
        for procurement in procurements:
            sale_line_id = procurement.values.get("sale_line_id")
            if sale_line_id:
                sale_line = self.env["sale.order.line"].browse(sale_line_id)
                if sale_line.dest_address_id:
                    procurement.values["partner_id"] = sale_line.dest_address_id.id
                    group = procurement.values.get("group_id")
                    group.partner_id = sale_line.dest_address_id
                    new_location_id = sale_line.dest_address_id.property_stock_customer
                else:
                    new_location_id = procurement.location_id
                new_procs.append(
                    Proc(
                        procurement.product_id,
                        procurement.product_qty,
                        procurement.product_uom,
                        new_location_id,
                        procurement.name,
                        procurement.origin,
                        procurement.company_id,
                        procurement.values,
                    )
                )
            else:
                new_procs.append(procurement)
        return super(ProcurementGroup, self).run(new_procs, raise_user_error)
