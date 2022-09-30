# Copyright 2020 ForgeFlow S.L.
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl.html).

from odoo import api, models


class ProcurementGroup(models.Model):
    _inherit = "procurement.group"

    @api.model
    def run(self, product_id, product_qty, product_uom, location_id, name,
            origin, values):
        sale_line_id = values.get("sale_line_id")
        if sale_line_id:
            sale_line = self.env["sale.order.line"].browse(sale_line_id)
            if sale_line.dest_address_id:
                values["partner_dest_id"] = sale_line.dest_address_id
                group = values.get("group_id")
                group.partner_id = sale_line.dest_address_id
                location_id = sale_line.dest_address_id.property_stock_customer
        return super(ProcurementGroup, self).run(
            product_id, product_qty, product_uom, location_id, name,
            origin, values,
        )
