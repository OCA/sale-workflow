# Copyright 2023 Akretion
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo import api, fields, models


class SaleOrder(models.Model):
    _inherit = "sale.order"

    warehouse_rule_need_change = fields.Html(
        compute="_compute_warehouse_rule_need_change"
    )
    show_sale_line_warehouse_column = fields.Boolean(
        related="company_id.show_sale_line_warehouse_column",
    )

    @api.depends("order_line.warehouse_id", "warehouse_id")
    def _compute_warehouse_rule_need_change(self):
        for rec in self:
            warehouses = rec.order_line.warehouse_id
            rec.warehouse_rule_need_change = (
                self.env._(
                    "The delivery will be sent from %s, "
                    "you can change the warehouse or "
                    "it will be done at the order confirmation.",
                    warehouses.name,
                )
                if len(warehouses) == 1 and warehouses != rec.warehouse_id
                else False
            )


class SaleOrderLine(models.Model):
    _inherit = "sale.order.line"

    warehouse_id = fields.Many2one(readonly=False)

    def _compute_warehouse_id(self):
        res = super()._compute_warehouse_id()
        for line in self:
            variant_warehouse = line.product_id.variant_warehouse_id.filtered(
                lambda w, line=line: w.company_id == line.order_id.company_id
            )
            if variant_warehouse:
                line.warehouse_id = variant_warehouse
        return res
