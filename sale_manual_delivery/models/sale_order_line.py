# Copyright 2017 Denis Leemann, Camptocamp SA
# Copyright 2021 Iván Todorovich, Camptocamp SA
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

from odoo import api, fields, models
from odoo.fields import Domain
from odoo.tools.float_utils import float_compare


class SaleOrderLine(models.Model):
    _inherit = "sale.order.line"

    qty_procured = fields.Float(
        string="Quantity Procured",
        help="Quantity already planned or shipped (stock movements already created)",
        compute="_compute_qty_procured",
        readonly=True,
        store=True,
    )
    qty_to_procure = fields.Float(
        string="Quantity to Procure",
        help="There is Pending qty to add to a delivery",
        compute="_compute_qty_to_procure",
        store=True,
        readonly=True,
    )

    @api.depends(
        "move_ids.state",
        "move_ids.scrap_id",
        "move_ids.product_uom_qty",
        "move_ids.product_uom",
        "move_ids.location_id",
        "move_ids.location_dest_id",
    )
    def _compute_qty_procured(self):
        """
        Computes the already planned quantities for the given sale order lines,
        based on the existing stock.moves
        """
        for line in self:
            qty_procured = 0
            if line.qty_delivered_method == "stock_move":
                qty_procured = line._get_qty_procurement()
            line.qty_procured = qty_procured

    @api.depends("product_uom_qty", "qty_procured")
    def _compute_qty_to_procure(self):
        """Computes the remaining quantity to plan on sale order lines"""
        for line in self:
            line.qty_to_procure = line.product_uom_qty - line.qty_procured

    def _get_stock_reference(self):
        # Overload to get the stock.reference for the right date / partner
        # Note: sale_manual_delivery is expected to be a manual.delivery record
        manual_delivery = self.env.context.get("sale_manual_delivery")
        if not manual_delivery:
            return super()._get_stock_reference()
        domain = Domain(
            [
                ("sale_ids", "in", self.order_id.id),
                ("partner_id", "=", manual_delivery.partner_id.id),
            ]
        )
        if manual_delivery.date_planned:
            domain += Domain("date_planned", "=", manual_delivery.date_planned)
        return self.env["stock.reference"].search(domain, limit=1)

    def _get_stock_reference_key(self):
        manual_delivery = self.env.context.get("sale_manual_delivery")
        if not manual_delivery:
            return super()._get_stock_reference_key()
        return (
            50,
            self.order_id.id,
            manual_delivery.partner_id.id,
            manual_delivery.date_planned,
        )

    def _prepare_reference_vals(self):
        # Overload to add manual.delivery fields to stock.reference
        # Note: sale_manual_delivery is expected to be a manual.delivery record
        res = super()._prepare_reference_vals()
        manual_delivery = self.env.context.get("sale_manual_delivery")
        if manual_delivery:
            res["partner_id"] = manual_delivery.partner_id.id
            res["date_planned"] = manual_delivery.date_planned
        return res

    def _prepare_procurement_values(self):
        # Overload to handle manual delivery date planned and route
        # This method ultimately prepares stock.move vals as its result is sent
        # to StockRule._get_stock_move_values.
        # Note: sale_manual_delivery is expected to be a manual.delivery record
        res = super()._prepare_procurement_values()
        if manual_delivery := self.env.context.get("sale_manual_delivery"):
            if date := manual_delivery.date_planned:
                res["date_planned"] = date
            if route := manual_delivery.route_id:
                # `_get_stock_move_values` expects a recordset
                res["route_ids"] = route
        return res

    def _action_launch_stock_rule_manual(self, *, previous_product_uom_qty=False):
        # Note: sale_manual_delivery is expected to be a manual.delivery record
        manual_delivery = self.env.context.get("sale_manual_delivery")
        precision = self.env["decimal.precision"].precision_get("Product Unit")
        procurements = []
        groups = {}
        if not previous_product_uom_qty:
            previous_product_uom_qty = {}
        for line in self:
            line = line.with_company(line.company_id)
            if line.state != "sale" or line.product_id.type != "consu":
                continue
            # Qty comes from the manual delivery wizard
            # This is different than the original method
            manual_line = manual_delivery.line_ids.filtered(
                lambda mdl, ln=line: mdl.order_line_id == ln
            )
            if (
                float_compare(
                    manual_line.quantity,
                    0,
                    precision_digits=precision,
                )
                <= 0
            ):
                continue

            group = line._get_stock_reference()
            if not group:
                group = groups.get(line._get_stock_reference_key())
            if not group:
                group = self.env["stock.reference"].create(
                    line._prepare_reference_vals()
                )
                groups[line._get_stock_reference_key()] = group

            values = line._prepare_procurement_values()
            values["reference_ids"] = group
            line_uom = line.product_uom_id
            quant_uom = line.product_id.uom_id
            product_qty, procurement_uom = line_uom._adjust_uom_quantities(
                manual_line.quantity, quant_uom
            )
            procurements += line._create_procurements(
                product_qty, procurement_uom, values
            )
            previous_product_uom_qty[line.id] = line.product_uom_qty
        if procurements:
            self.env["stock.rule"].run(procurements)
        return True

    def _action_launch_stock_rule(self, *, previous_product_uom_qty=False):
        # Overload to skip launching stock rules on manual delivery lines
        # We only launch them when this is called from the manual delivery wizard
        # Note: sale_manual_delivery is expected to be a manual.delivery record
        manual_delivery_lines = self.filtered("order_id.manual_delivery")
        lines_to_launch = self - manual_delivery_lines
        return super(SaleOrderLine, lines_to_launch)._action_launch_stock_rule(
            previous_product_uom_qty=previous_product_uom_qty
        )
