# Copyright 2018 ACSONE SA/NV
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo import api, fields, models
from odoo.tools import float_compare


class SaleOrderLine(models.Model):

    _inherit = "sale.order.line"

    to_be_procured = fields.Boolean(
        compute="_compute_to_be_procured",
        help="Technical field that check if the whole order line quantities"
        "have the corresponding stock moves quantities in order to fullfill"
        "demand.",
    )
    pickings_in_progress = fields.Boolean(compute="_compute_pickings_in_progress")

    can_amend_and_reprocure = fields.Boolean(
        compute="_compute_can_amend_and_reprocure",
    )

    @api.model
    def _get_can_amend_and_reprocure_depends(self):
        return ["pickings_in_progress", "product_id.type"]

    @api.depends(lambda self: self._get_can_amend_and_reprocure_depends())
    def _compute_can_amend_and_reprocure(self):
        """
            Filter here the lines that can be reprocured

        :return: [description]
        :rtype: [type]
        """
        lines_can_reprocure = self.filtered(
            lambda line: not line.pickings_in_progress
            and line.product_id.type != "service"
        )
        lines_can_reprocure.update({"can_amend_and_reprocure": True})
        (self - lines_can_reprocure).update({"can_amend_and_reprocure": False})

    @api.depends(
        "order_id.picking_ids.can_be_amended",
        "chained_move_ids.picking_id.can_be_amended",
    )
    def _compute_pickings_in_progress(self):
        """
        Compute the picking in progress. That depends on picking
        'can_be_amended' state. If one is not in the 'can_be_amended' state,
        we are in the 'pickings_in_progress' situation.
        :return:
        """
        line_in_progres = self.filtered(
            lambda l: any(
                picking.state != "cancel" and not picking.can_be_amended
                for picking in (l.chained_move_ids | l.move_ids).mapped("picking_id")
            )
        )
        line_in_progres.update({"pickings_in_progress": True})
        (self - line_in_progres).update({"pickings_in_progress": False})

    @api.depends(
        "move_ids",
        "move_ids.state",
        "move_ids.product_qty",
        "product_uom_qty",
    )
    def _compute_to_be_procured(self):
        """
        This compare the current procurement quantities (see Odoo
        _action_procurement_create function)
        :return:
        """
        precision = self.env["decimal.precision"].precision_get(
            "Product Unit of Measure"
        )
        for line in self:
            qty = 0.0
            for proc in line.move_ids.filtered(lambda p: p.state != "cancel"):
                qty += proc.product_qty
            if float_compare(qty, line.product_uom_qty, precision_digits=precision) < 0:
                line.to_be_procured = True
            else:
                line.to_be_procured = False

    def _amend_and_reprocure(self):
        """
        Filter lines that can reprocure
        Cancel related moves
        Relaunch stock rules
        """
        lines = self.filtered("can_amend_and_reprocure")
        moves = lines.mapped("move_ids") | lines.mapped("move_ids.move_orig_ids")
        moves._action_cancel()
        lines.filtered(
            lambda line: line.state == "sale" and line.to_be_procured
        )._action_launch_stock_rule()

    def write(self, values):
        precision = self.env["decimal.precision"].precision_get(
            "Product Unit of Measure"
        )
        lines_lower = self.env["sale.order.line"].browse()
        if "product_uom_qty" in values:
            lines_lower = self.filtered(
                lambda l: l.state == "sale"
                and float_compare(
                    l.product_uom_qty,
                    values["product_uom_qty"],
                    precision_digits=precision,
                )
                > 0
            )
        res = super(SaleOrderLine, self).write(values)
        if "product_uom_qty" in values:
            # Quantities has changed
            # Check if procurement has to be created
            lines_lower._amend_and_reprocure()
        return res
