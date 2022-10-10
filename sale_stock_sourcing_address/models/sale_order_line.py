# Copyright 2019 Eficent Business and IT Consulting Services, S.L.
# License LGPL-3.0 or later (https://www.gnu.org/licenses/lgpl.html).

from odoo import api, fields, models


class SaleOrderLine(models.Model):
    _inherit = "sale.order.line"

    sourcing_address_id = fields.Many2one(
        "res.partner", string="Sourcing Address", compute="_compute_sourcing_address_id"
    )

    warehouse_id = fields.Many2one(
        "stock.warehouse", string="Order's Warehouse", related="order_id.warehouse_id"
    )

    def _prepare_procurement_values_for_sourcing(self, group_id=False):
        self.ensure_one()
        values = {
            "company_id": self.order_id.company_id,
            "group_id": group_id,
            "sale_line_id": self.id,
            "route_ids": self.route_id,
            "warehouse_id": self.warehouse_id or False,
            "partner_dest_id": self.order_id.partner_shipping_id,
        }
        return values

    @api.onchange("route_id", "order_id", "product_id", "warehouse_id")
    def _compute_sourcing_address_id(self):
        for line in self:
            line.sourcing_address_id = False
            values = line._prepare_procurement_values_for_sourcing()
            rule = self.env["procurement.group"]._get_rule(
                line.product_id,
                line.order_id.partner_shipping_id.property_stock_customer,
                values,
            )
            if rule:
                source_wh = rule.propagate_warehouse_id or rule.warehouse_id
                line.sourcing_address_id = source_wh.partner_id
