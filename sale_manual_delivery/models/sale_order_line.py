# Copyright 2017 Denis Leemann, Camptocamp SA
# Copyright 2021 Iván Todorovich, Camptocamp SA
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

from odoo import api, fields, models


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
        "move_ids.scrapped",
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
            if line.qty_delivered_method == "stock_move":
                line.qty_procured = line._get_qty_procurement(
                    previous_product_uom_qty=False
                )

    @api.depends("product_uom_qty", "qty_procured")
    def _compute_qty_to_procure(self):
        """Computes the remaining quantity to plan on sale order lines"""
        for line in self:
            line.qty_to_procure = line.product_uom_qty - line.qty_procured

    def _get_procurement_group(self):
        # Overload to get the procurement.group for the right date / partner
        # Note: sale_manual_delivery is expected to be a manual.delivery record
        manual_delivery = self.env.context.get("sale_manual_delivery")
        if manual_delivery:
            domain = [
                ("sale_id", "=", self.order_id.id),
                ("partner_id", "=", manual_delivery.partner_id.id),
            ]
            if manual_delivery.date_planned:
                domain += [
                    ("date_planned", "=", manual_delivery.date_planned),
                ]
            return self.env["procurement.group"].search(domain, limit=1)
        else:
            return super()._get_procurement_group()

    def _prepare_procurement_group_vals(self):
        # Overload to add manual.delivery fields to procurement.group
        # Note: sale_manual_delivery is expected to be a manual.delivery record
        res = super()._prepare_procurement_group_vals()
        manual_delivery = self.env.context.get("sale_manual_delivery")
        if manual_delivery:
            res["partner_id"] = manual_delivery.partner_id.id
            res["date_planned"] = manual_delivery.date_planned
        return res

    def _prepare_procurement_values(self, group_id=False):
        # Overload to handle manual delivery date planned and route
        # This method ultimately prepares stock.move vals as its result is sent
        # to StockRule._get_stock_move_values.
        # Note: sale_manual_delivery is expected to be a manual.delivery record
        res = super()._prepare_procurement_values(group_id=group_id)
        manual_delivery = self.env.context.get("sale_manual_delivery")
        if manual_delivery:
            if manual_delivery.date_planned:
                res["date_planned"] = manual_delivery.date_planned
            if manual_delivery.route_id:
                # `_get_stock_move_values` expects a recordset
                res["route_ids"] = manual_delivery.route_id
        return res

    def _action_launch_stock_rule_manual(self, previous_product_uom_qty=False):
        # Note: sale_manual_delivery is expected to be a manual.delivery record
        manual_delivery = self.env.context.get("sale_manual_delivery")
        procurements = []
        for line in self:
            if line.state != "sale" or line.product_id.type not in ("consu", "product"):
                continue
            # Qty comes from the manual delivery wizard
            # This is different than the original method
            manual_line = manual_delivery.line_ids.filtered(
                lambda l: l.order_line_id == line
            )
            if not manual_line.quantity:
                continue
            group_id = line._get_procurement_group()
            if not group_id:
                group_id = self.env["procurement.group"].create(
                    line._prepare_procurement_group_vals()
                )
            else:
                # In case the procurement group is already created and the order was
                # cancelled, we need to update certain values of the group.
                # This part is different than the original method
                if group_id.move_type != line.order_id.picking_policy:
                    group_id.write({"move_type": line.order_id.picking_policy})
            values = line._prepare_procurement_values(group_id=group_id)
            line_uom = line.product_uom
            quant_uom = line.product_id.uom_id
            product_qty, procurement_uom = line_uom._adjust_uom_quantities(
                manual_line.quantity, quant_uom
            )
            procurements.append(
                self.env["procurement.group"].Procurement(
                    line.product_id,
                    product_qty,
                    procurement_uom,
                    line.order_id.partner_shipping_id.property_stock_customer,
                    line.name,
                    line.order_id.name,
                    line.order_id.company_id,
                    values,
                )
            )
        if procurements:
            self.env["procurement.group"].run(procurements)
        return True

    def _action_launch_stock_rule(self, previous_product_uom_qty=False):
        # Overload to skip launching stock rules on manual delivery lines
        # We only launch them when this is called from the manual delivery wizard
        # Note: sale_manual_delivery is expected to be a manual.delivery record
        manual_delivery_lines = self.filtered("order_id.manual_delivery")
        lines_to_launch = self - manual_delivery_lines
        return super(SaleOrderLine, lines_to_launch)._action_launch_stock_rule(
            previous_product_uom_qty=previous_product_uom_qty
        )
