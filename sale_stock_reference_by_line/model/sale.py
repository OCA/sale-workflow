# Copyright 2013-2014 Camptocamp SA - Guewen Baconnier
# © 2016-20 ForgeFlow S.L. (https://www.forgeflow.com)
# © 2016 Serpent Consulting Services Pvt. Ltd.
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo import fields, models
from odoo.tools.float_utils import float_compare


class SaleOrderLine(models.Model):
    _inherit = "sale.order.line"

    stock_reference_id = fields.Many2one(
        "stock.reference", "Procurement Reference", copy=False
    )

    def _get_stock_reference(self):
        return self.stock_reference_id or False

    def _get_stock_reference_key(self):
        """Return a key with priority to be used to regroup lines in multiple
        procurement groups

        """
        return 8, self.order_id.id

    def _prepare_procurement_values(self):
        # Overload core method to modify stock references to the line specific
        values = super()._prepare_procurement_values()
        values["reference_ids"] = self.stock_reference_id
        return values

    def _action_launch_stock_rule(self, *, previous_product_uom_qty=False):
        """
        Launch procurement group run method.
        """
        if self.env.context.get("skip_procurement"):
            return True
        precision = self.env["decimal.precision"].precision_get("Product Unit")
        procurements = []
        groups = {}
        if not previous_product_uom_qty:
            previous_product_uom_qty = {}
        for line in self:
            line = line.with_company(line.company_id)
            if (
                line.state != "sale"
                or line.order_id.locked
                or line.product_id.type != "consu"
            ):
                continue
            qty = line._get_qty_procurement(previous_product_uom_qty)
            if (
                float_compare(qty, line.product_uom_qty, precision_digits=precision)
                == 0
            ):
                continue

            group = line._get_stock_reference()

            # Group the sales order lines with same procurement group
            # according to the group key
            for order_line in line.order_id.order_line:
                line_group = order_line.stock_reference_id or False
                if line_group:
                    groups[order_line._get_stock_reference_key()] = line_group
            if not group:
                group = groups.get(line._get_stock_reference_key())

            if not group:
                vals = line._prepare_reference_vals()
                group = self.env["stock.reference"].create(vals)

            line.stock_reference_id = group

            values = line._prepare_procurement_values()
            product_qty = line.product_uom_qty - qty

            line_uom = line.product_uom_id
            quant_uom = line.product_id.uom_id
            product_qty, procurement_uom = line_uom._adjust_uom_quantities(
                product_qty, quant_uom
            )
            procurements += line._create_procurements(
                product_qty, procurement_uom, values
            )
            # We store the procured quantity in the UoM of the line to avoid
            # duplicated procurements, specially for dropshipping and kits.
            previous_product_uom_qty[line.id] = line.product_uom_qty
        if procurements:
            self.env["stock.rule"].run(procurements)
        # This next block is currently needed only because the scheduler trigger is done
        # by picking confirmation rather than stock.move confirmation
        orders = self.mapped("order_id")
        for order in orders:
            pickings_to_confirm = order.picking_ids.filtered(
                lambda p: p.state not in ["cancel", "done"]
            )
            if pickings_to_confirm:
                # Trigger the Scheduler for Pickings
                pickings_to_confirm.action_confirm()
        return super(
            SaleOrderLine, self.with_context(sale_group_by_line=True)
        )._action_launch_stock_rule(previous_product_uom_qty=previous_product_uom_qty)
