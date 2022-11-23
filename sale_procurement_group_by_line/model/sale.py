# Copyright 2013-2014 Camptocamp SA - Guewen Baconnier
# © 2016-20 ForgeFlow S.L. (https://www.forgeflow.com)
# © 2016 Serpent Consulting Services Pvt. Ltd.
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo import fields, models
from odoo.tools.float_utils import float_compare


class SaleOrderLine(models.Model):
    _inherit = "sale.order.line"

    procurement_group_id = fields.Many2one(
        "procurement.group", "Procurement group", copy=False
    )

    def _get_procurement_group(self):
        super()._get_procurement_group()
        return self.procurement_group_id or False

    def _get_procurement_group_key(self):
        """Return a key with priority to be used to regroup lines in multiple
        procurement groups

        """
        return 8, self.order_id.id

    def _action_launch_stock_rule(self, previous_product_uom_qty=False):
        """
        Launch procurement group run method.
        """
        precision = self.env["decimal.precision"].precision_get(
            "Product Unit of Measure"
        )
        procurements = []
        groups = {}
        if not previous_product_uom_qty:
            previous_product_uom_qty = {}
        for line in self:
            line = line.with_company(line.company_id)
            if line.state != "sale" or line.product_id.type not in ("consu", "product"):
                continue
            qty = line._get_qty_procurement(previous_product_uom_qty)
            if (
                float_compare(qty, line.product_uom_qty, precision_digits=precision)
                >= 0
            ):
                continue

            group_id = line._get_procurement_group()

            # Group the sales order lines with same procurement group
            # according to the group key
            for order_line in line.order_id.order_line:
                g_id = order_line.procurement_group_id or False
                if g_id:
                    groups[order_line._get_procurement_group_key()] = g_id
            if not group_id:
                group_id = groups.get(line._get_procurement_group_key())

            if not group_id:
                vals = line._prepare_procurement_group_vals()
                group_id = self.env["procurement.group"].create(vals)
            else:
                # In case the procurement group is already created and the
                # order was cancelled, we need to update certain values
                # of the group.
                updated_vals = {}
                if group_id.partner_id != line.order_id.partner_shipping_id:
                    updated_vals.update(
                        {"partner_id": line.order_id.partner_shipping_id.id}
                    )
                if group_id.move_type != line.order_id.picking_policy:
                    updated_vals.update({"move_type": line.order_id.picking_policy})
                if updated_vals:
                    group_id.write(updated_vals)
            line.procurement_group_id = group_id

            values = line._prepare_procurement_values(group_id=group_id)
            product_qty = line.product_uom_qty - qty

            line_uom = line.product_uom
            quant_uom = line.product_id.uom_id
            product_qty, procurement_uom = line_uom._adjust_uom_quantities(
                product_qty, quant_uom
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
            # We store the procured quantity in the UoM of the line to avoid
            # duplicated procurements, specially for dropshipping and kits.
            previous_product_uom_qty[line.id] = line.product_uom_qty
        if procurements:
            self.env["procurement.group"].run(procurements)
        return super(
            SaleOrderLine, self.with_context(sale_group_by_line=True)
        )._action_launch_stock_rule(previous_product_uom_qty=previous_product_uom_qty)
