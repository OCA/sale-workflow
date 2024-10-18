# Copyright 2023 Akretion
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo import _, api, fields, models


class SaleOrder(models.Model):
    _inherit = "sale.order"

    warehouse_rule_need_change = fields.Html(
        readonly=True, compute="_compute_warehouse_rule_message"
    )
    warehouse_rule_info = fields.Html(
        readonly=True, compute="_compute_warehouse_rule_message"
    )

    @api.depends("order_line.product_id.variant_warehouse_id", "warehouse_id")
    def _compute_warehouse_rule_message(self):
        for rec in self:
            rec.warehouse_rule_need_change = False
            rec.warehouse_rule_info = False
            if not rec.order_line:
                continue
            warehouse_ids = rec.order_line.mapped("product_id.variant_warehouse_id")
            if (
                len(warehouse_ids) == 1
                and warehouse_ids != rec.warehouse_id
                and all(
                    product.variant_warehouse_id
                    for product in rec.order_line.product_id
                )
            ):
                rec.warehouse_rule_need_change = _(
                    """The delivery will be sent from %s,
                    you can change the warehouse or
                    it will be done at the order confirmation.""",
                    warehouse_ids.name,
                )
            elif len(warehouse_ids) > 1 or (
                len(warehouse_ids) == 1
                and any(
                    product
                    for product in rec.order_line.product_id
                    if not product.variant_warehouse_id
                )
                and rec.warehouse_id not in warehouse_ids
            ):
                warehouses = warehouse_ids + rec.warehouse_id
                rec.warehouse_rule_info = _(
                    "The delivery will be sent from multiple warehouses: "
                    + ", ".join(warehouses.mapped("name"))
                )

    def action_confirm(self):
        for rec in self:
            if rec.warehouse_rule_need_change:
                warehouse_id = rec.order_line.mapped("product_id.variant_warehouse_id")
                rec.warehouse_id = warehouse_id
        return super().action_confirm()


class SaleOrderLine(models.Model):
    _inherit = "sale.order.line"

    def _prepare_procurement_values(self, group_id=False):
        values = super()._prepare_procurement_values(group_id=group_id)
        for line in self:
            variant_warehouse = line.product_id.variant_warehouse_id
            if variant_warehouse:
                values["warehouse_id"] = variant_warehouse
        return values
