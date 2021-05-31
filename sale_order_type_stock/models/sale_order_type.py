# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo import api, fields, models


class SaleOrderType(models.Model):
    _inherit = "sale.order.type"

    @api.model
    def _get_selection_picking_policy(self):
        return self.env["sale.order"].fields_get(allfields=["picking_policy"])[
            "picking_policy"
        ]["selection"]

    def default_picking_policy(self):
        default_dict = self.env["sale.order"].default_get(["picking_policy"])
        return default_dict.get("picking_policy")

    warehouse_id = fields.Many2one(
        comodel_name="stock.warehouse",
        string="Warehouse",
        sale_order_field="warehouse_id",
    )
    picking_policy = fields.Selection(
        selection="_get_selection_picking_policy",
        string="Shipping Policy",
        default=default_picking_policy,
        sale_order_field="picking_policy",
    )
    incoterm_id = fields.Many2one(
        comodel_name="account.incoterms", string="Incoterm", sale_order_field="incoterm"
    )
    route_id = fields.Many2one(
        "stock.location.route",
        string="Route",
        domain=[("sale_selectable", "=", True)],
        ondelete="restrict",
        check_company=True,
    )
