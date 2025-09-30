# Copyright 2025 Tecnativa - Eduardo Ezerouali
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl)

from odoo import api, fields, models


class SaleOrder(models.Model):
    _inherit = "sale.order"

    warehouse_id = fields.Many2one(
        "stock.warehouse",
        string="Warehouse",
        required=True,
        readonly=True,
        states={"draft": [("readonly", False)], "sent": [("readonly", False)]},
        compute="_compute_warehouse_id",
        store=True,
        check_company=True,
    )

    @api.depends("partner_shipping_id", "partner_id")
    def _compute_warehouse_id(self):
        for order in self:
            if order.partner_shipping_id.sale_warehouse_id:
                order.warehouse_id = order.partner_shipping_id.sale_warehouse_id
            elif order.partner_id.sale_warehouse_id:
                order.warehouse_id = order.partner_id.sale_warehouse_id
