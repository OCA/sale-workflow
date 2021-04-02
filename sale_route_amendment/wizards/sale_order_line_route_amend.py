# Copyright 2020 ACSONE SA/NV
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo import _, api, fields, models


class SaleOrderLineRouteAmend(models.TransientModel):

    _name = "sale.order.line.route.amend"
    _description = "Sale Order Line Route Amendment"

    order_id = fields.Many2one(
        comodel_name="sale.order", string="Order", required=True, ondelete="cascade",
    )
    order_line_ids = fields.Many2many(
        string="Sale Order Lines", comodel_name="sale.order.line", required=True
    )
    route_id = fields.Many2one(
        comodel_name="stock.location.route",
        domain=[("sale_selectable", "=", True)],
        required=True,
        string="New Route",
    )
    is_updatable = fields.Boolean()
    warning = fields.Text()

    @api.model
    def default_get(self, fields_list):
        res = super().default_get(fields_list)
        order_id = self.env.context.get("active_id", [])
        order = self.env["sale.order"].browse(order_id)
        # See sale_procurement_amendment
        sale_line_ids = order.order_line.filtered("can_amend_and_reprocure")
        res["order_id"] = order_id
        res["order_line_ids"] = sale_line_ids.ids
        res["is_updatable"] = bool(sale_line_ids)
        if not bool(sale_line_ids):
            res["warning"] = _(
                "Route updating is not possible as some logistics "
                "actions have been processed or partially processed "
                "for all lines."
            )
        return res

    def update_route(self):
        """We update the route on selected sale order lines and launch the
           re-procurement

        :return: [description]
        :rtype: [type]
        """
        for wizard in self:
            wizard.order_line_ids.write({"route_id": wizard.route_id.id})
            wizard.order_line_ids._amend_and_reprocure()
        return True
