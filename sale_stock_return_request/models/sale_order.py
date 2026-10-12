# Copyright 2023 Solvos Consultoría Informática
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl.html).
import ast

from odoo import fields, models
from odoo.tools import float_compare


class SaleOrder(models.Model):
    _inherit = "sale.order"

    show_create_return_request = fields.Boolean(
        compute="_compute_show_create_return_request",
    )

    def _get_returnable_lines(self):
        return self.order_line.filtered(
            lambda x: not x.display_type
            and x.product_id.type != "service"
            and float_compare(
                x.qty_delivered, 0.0, precision_rounding=x.product_uom.rounding
            )
            > 0
        )

    def _compute_show_create_return_request(self):
        for order in self:
            order.show_create_return_request = len(order._get_returnable_lines()) > 0

    def action_create_return_request(self):
        self.ensure_one()
        action = self.env["ir.actions.act_window"]._for_xml_id(
            "sale_stock_return_request.action_sale_stock_return_request_tree"
        )
        action["views"] = [
            (
                self.env.ref("stock_return_request.view_stock_return_request_form").id,
                "form",
            )
        ]
        action["context"] = {
            **ast.literal_eval(action["context"]),
            "default_partner_id": self.partner_id.id,
            "default_filter_sale_order_ids": [(4, self.id)],
            "default_line_ids": [
                (0, 0, {"product_id": line.product_id.id})
                for line in self._get_returnable_lines()
            ],
        }
        return action
