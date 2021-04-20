# Copyright 2017 Denis Leemann, Camptocamp SA
# Copyright 2021 Iván Todorovich, Camptocamp SA
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

from odoo import _, api, fields, models
from odoo.exceptions import UserError


class ManualDelivery(models.TransientModel):
    _name = "manual.delivery"
    _description = "Manual Delivery"
    _order = "create_date desc"

    @api.model
    def default_get(self, fields):
        res = super().default_get(fields)
        # Get lines from active_model if it's a sale.order / sale.order.line
        sale_lines = self.env["sale.order.line"]
        active_model = self.env.context["active_model"]
        if active_model == "sale.order.line":
            sale_ids = self.env.context["active_ids"] or []
            sale_lines = self.env["sale.order.line"].browse(sale_ids)
        elif active_model == "sale.order":
            sale_ids = self.env.context["active_ids"] or []
            sale_lines = self.env["sale.order"].browse(sale_ids).mapped("order_line")
        if len(sale_lines.mapped("order_id.partner_id")) > 1:
            raise UserError(_("Please select one partner at a time"))
        if sale_lines:
            # Get partner from those lines
            partner = sale_lines.mapped("order_id.partner_id")
            res["partner_id"] = partner.id
            res["commercial_partner_id"] = partner.commercial_partner_id.id
            # Convert to manual.delivery.lines
            res["line_ids"] = [
                (
                    0,
                    0,
                    {
                        "order_line_id": line.id,
                        "name": line.name,
                        "product_id": line.product_id.id,
                        "qty_ordered": line.product_uom_qty,
                        "qty_procured": line.qty_procured,
                        "quantity": line.qty_to_procure,
                    },
                )
                for line in sale_lines
                if line.qty_to_procure and line.product_id.type != "service"
            ]
        return res

    commercial_partner_id = fields.Many2one(
        "res.partner", required=True, readonly=True, ondelete="cascade",
    )
    partner_id = fields.Many2one(
        "res.partner",
        string="Delivery Address",
        domain="""
            [
                "|",
                ("id", "=", commercial_partner_id),
                ("parent_id", "=", commercial_partner_id),
            ],
        """,
        ondelete="cascade",
    )
    carrier_id = fields.Many2one(
        "delivery.carrier", string="Delivery Method", ondelete="cascade",
    )
    route_id = fields.Many2one(
        "stock.location.route",
        string="Use specific Route",
        domain=[("sale_selectable", "=", True)],
        ondelete="cascade",
        help="Leave it blank to use the same route that is in the sale line",
    )
    line_ids = fields.One2many(
        "manual.delivery.line", "manual_delivery_id", string="Lines to validate",
    )
    date_planned = fields.Datetime(string="Date Planned")

    def confirm(self):
        """ Creates the manual procurements """
        self.ensure_one()
        sale_order_lines = self.line_ids.mapped("order_line_id")
        sale_order_lines.with_context(
            sale_manual_delivery=self
        )._action_launch_stock_rule_manual()
