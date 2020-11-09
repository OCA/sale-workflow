# Copyright 2017 Denis Leemann, Camptocamp SA
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

from odoo import api, fields, models
from odoo.exceptions import UserError
from odoo.tools import float_compare, float_is_zero
from odoo.tools.translate import _

PARTNER_DOMAIN = """[
    "|", ("id", "=", commercial_partner_id),
    ("parent_id", "=", commercial_partner_id),
]"""


class ManualDelivery(models.TransientModel):
    """Creates procurements manually"""

    _name = "manual.delivery"
    _description = "Manual Delivery"
    _order = "create_date desc"

    @api.model
    def default_get(self, fields):
        if "line_ids" not in fields:
            return {}
        res = super(ManualDelivery, self).default_get(fields)
        active_model = self.env.context["active_model"]
        if active_model == "sale.order.line":
            sale_ids = self.env.context["active_ids"] or []
            sale_lines = (
                self.env["sale.order.line"]
                .browse(sale_ids)
                .filtered(lambda s: s.pending_qty_to_deliver)
            )
        elif active_model == "sale.order":
            sale_ids = self.env.context["active_ids"] or []
            sale_lines = (
                self.env["sale.order"]
                .browse(sale_ids)
                .mapped("order_line")
                .filtered(lambda s: s.pending_qty_to_deliver)
            )
        if len(sale_lines.mapped("order_id.partner_id")) > 1:
            raise UserError(_("Please select one partner at a time"))
        res["line_ids"] = self.fill_lines(sale_lines)
        partner = sale_lines.mapped("order_id.partner_id")
        res["partner_id"] = partner.id
        res["commercial_partner_id"] = partner.commercial_partner_id.id
        return res

    def fill_lines(self, sale_lines):
        lines = []

        for line in sale_lines:
            if (
                not line.existing_qty == line.product_uom_qty
                and line.product_id.type != "service"
            ):
                vals = {
                    "product_id": line.product_id.id,
                    "line_description": line.product_id.name,
                    "order_line_id": line.id,
                    "ordered_qty": line.product_uom_qty,
                    "existing_qty": line.existing_qty,
                    "to_ship_qty": line.product_uom_qty - line.existing_qty,
                }
                lines.append((0, 0, vals))
        return lines

    date_planned = fields.Date(string="Date Planned")
    line_ids = fields.One2many(
        "manual.delivery.line", "manual_delivery_id", string="Lines to validate",
    )
    carrier_id = fields.Many2one("delivery.carrier", string="Delivery Method")
    route_id = fields.Many2one(
        "stock.location.route",
        string="Use specific Route",
        domain=[("sale_selectable", "=", True)],
        ondelete="restrict",
        help="Leave it blank to use the same route that is in the sale line",
    )

    partner_id = fields.Many2one(
        "res.partner", domain=PARTNER_DOMAIN, string="Delivery Address"
    )
    commercial_partner_id = fields.Many2one("res.partner")

    def record_picking(self):
        for wizard in self:
            if not wizard.line_ids:
                continue
            date_planned = wizard.date_planned
            proc_list_to_run_by_order_id = {}
            for wizard_line in wizard.line_ids:
                uom_rounding = wizard_line.product_id.uom_id.rounding

                if (
                    float_compare(
                        wizard_line.to_ship_qty,
                        wizard_line.ordered_qty - wizard_line.existing_qty,
                        precision_rounding=uom_rounding,
                    )
                    > 0.0
                ):
                    raise UserError(
                        _(
                            "You can not deliver more than the "
                            "remaining quantity. If you need to do "
                            "so, please edit the sale order first."
                        )
                    )
                orderline = wizard_line.order_line_id
                order = orderline.order_id
                group_id = order.procurement_group_id
                if not group_id:
                    group_id = orderline._get_procurement_group()
                    if not group_id:
                        procurement_group_vals = (
                            orderline._prepare_procurement_group_vals()
                        )
                        if date_planned:
                            procurement_group_vals["date_planned"] = date_planned
                            procurement_group_vals["sale_id"] = order.id
                        group_id = self.env["procurement.group"].create(
                            procurement_group_vals
                        )
                else:
                    group_id = self.env["procurement.group"].search(
                        [
                            ("sale_id", "=", order.id),
                            ("date_planned", "=", date_planned),
                        ],
                        limit=1,
                    )
                    if not group_id:
                        group_id = order.procurement_group_id.copy(
                            {"date_planned": date_planned}
                        )

                order.procurement_group_id = group_id
                vals = orderline._prepare_procurement_values(group_id=group_id)
                if wizard.date_planned:
                    vals["date_planned"] = date_planned
                    vals["sale_id"] = order.id
                if wizard.route_id:
                    vals["route_ids"] = wizard.route_id
                # Prepare this procurements
                line_uom = orderline.product_uom
                quant_uom = orderline.product_id.uom_id
                product_qty, procurement_uom = line_uom._adjust_uom_quantities(
                    wizard_line.to_ship_qty, quant_uom
                )
                if not float_is_zero(
                    product_qty, precision_rounding=procurement_uom.rounding
                ):
                    procurement = self.env["procurement.group"].Procurement(
                        wizard_line.product_id,
                        product_qty,
                        procurement_uom,
                        order.partner_shipping_id.property_stock_customer,
                        orderline.name,
                        order.name,
                        order.company_id,
                        vals,
                    )

                    if order not in proc_list_to_run_by_order_id:
                        proc_list_to_run_by_order_id[order] = [procurement]
                    else:
                        proc_list_to_run_by_order_id[order].append(procurement)

            for order, procument_list in proc_list_to_run_by_order_id.items():
                carrier_id = (
                    wizard.carrier_id if wizard.carrier_id else order.carrier_id
                )
                picking_vals = {
                    "carrier_id": carrier_id.id,
                }
                if wizard.partner_id:
                    picking_vals["partner_id"] = wizard.partner_id.id
                # Run the procurements
                self.env["procurement.group"].with_context(
                    picking_vals=picking_vals
                ).run(procument_list)
