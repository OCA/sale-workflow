# Copyright 2014-2021 Akretion France (http://www.akretion.com)
# @author Alexis de Lattre <alexis.delattre@akretion.com>
# Copyright 2016-2021 Sodexis (http://sodexis.com)
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

import logging

from odoo import api, fields, models

logger = logging.getLogger(__name__)


class SaleRental(models.Model):
    _name = "sale.rental"
    _description = "Rental"
    _order = "id desc"

    @api.depends(
        "start_order_line_id",
        "extension_order_line_ids.end_date",
        "extension_order_line_ids.state",
        "start_order_line_id.end_date",
    )
    def name_get(self):
        res = []
        for rental in self:
            name = "[%s] %s - %s > %s (%s)" % (
                rental.partner_id.display_name,
                rental.rented_product_id.display_name,
                rental.start_date,
                rental.end_date,
                rental._fields["state"].convert_to_export(rental.state, rental),
            )
            res.append((rental.id, name))
        return res

    @api.depends(
        "sell_order_line_ids.move_ids.state",
        "start_order_line_id.order_id.state",
        "start_order_line_id.move_ids.state",
        "start_order_line_id.move_ids.move_dest_ids.state",
    )
    def _compute_move_and_state(self):
        for rental in self:
            in_move = False
            out_move = False
            sell_move = False
            state = False
            if rental.start_order_line_id:
                for move in rental.start_order_line_id.move_ids:
                    if move.state != "cancel" and move.picking_code == "outgoing":
                        out_move = move
                    if move.move_dest_ids:
                        out_move = move
                        in_move = move.move_dest_ids[0]
                if (
                    rental.sell_order_line_ids
                    and rental.sell_order_line_ids[0].move_ids
                ):
                    sell_move = rental.sell_order_line_ids[0].move_ids[-1]
                state = "ordered"
                if out_move and out_move.state == "done":
                    state = "out"
                    if in_move:
                        if in_move.state == "done":
                            state = "in"
                        elif in_move.state == "cancel" and sell_move:
                            state = "sell_progress"
                            if sell_move.state == "done":
                                state = "sold"
                    elif sell_move:
                        state = "sell_progress"
                        if sell_move.state == "done":
                            state = "sold"
                        elif sell_move.state == "cancel":
                            state = "out"
                if rental.start_order_line_id.state == "cancel":
                    state = "cancel"
            rental.in_move_id = in_move
            rental.out_move_id = out_move
            rental.state = state
            rental.sell_move_id = sell_move

    @api.depends(
        "extension_order_line_ids.end_date",
        "extension_order_line_ids.state",
        "start_order_line_id.end_date",
    )
    def _compute_end_date(self):
        for rental in self:
            end_date = False
            if rental.start_order_line_id:
                end_date = rental.start_order_line_id.end_date

            for extension in rental.extension_order_line_ids:
                if (
                    extension.state in ("sale", "done")
                    and end_date
                    and extension.end_date
                    and extension.end_date > end_date
                ):
                    end_date = extension.end_date
            rental.end_date = end_date

    start_order_line_id = fields.Many2one(
        "sale.order.line", string="Rental SO Line", readonly=True
    )
    start_date = fields.Date(
        related="start_order_line_id.start_date", readonly=True, store=True
    )
    rental_product_id = fields.Many2one(
        "product.product",
        related="start_order_line_id.product_id",
        string="Rental Service",
        readonly=True,
        store=True,
    )
    rented_product_id = fields.Many2one(
        "product.product",
        related="start_order_line_id.product_id.rented_product_id",
        string="Rented Product",
        readonly=True,
        store=True,
    )
    rental_qty = fields.Float(
        related="start_order_line_id.rental_qty", readonly=True, store=True
    )
    start_order_id = fields.Many2one(
        "sale.order",
        related="start_order_line_id.order_id",
        string="Rental SO",
        readonly=True,
        store=True,
    )
    company_id = fields.Many2one(
        "res.company",
        related="start_order_line_id.company_id",
        string="Company",
        readonly=True,
        store=True,
    )
    partner_id = fields.Many2one(
        "res.partner",
        related="start_order_line_id.order_id.partner_id",
        string="Customer",
        readonly=True,
        store=True,
    )
    out_move_id = fields.Many2one(
        "stock.move",
        compute="_compute_move_and_state",
        string="Outgoing Move",
        readonly=True,
        store=True,
    )
    in_move_id = fields.Many2one(
        "stock.move",
        compute="_compute_move_and_state",
        string="Incoming Move",
        readonly=True,
        store=True,
    )
    out_state = fields.Selection(
        related="out_move_id.state", string="Out Move State", readonly=True
    )
    in_state = fields.Selection(
        related="in_move_id.state", string="In Move State", readonly=True
    )
    out_picking_id = fields.Many2one(
        "stock.picking",
        related="out_move_id.picking_id",
        string="Delivery Order",
        readonly=True,
    )
    in_picking_id = fields.Many2one(
        "stock.picking",
        related="in_move_id.picking_id",
        string="Receipt",
        readonly=True,
    )
    extension_order_line_ids = fields.One2many(
        "sale.order.line",
        "extension_rental_id",
        string="Rental Extensions",
        readonly=True,
    )
    sell_order_line_ids = fields.One2many(
        "sale.order.line", "sell_rental_id", string="Sell Rented Product", readonly=True
    )
    sell_move_id = fields.Many2one(
        "stock.move",
        compute="_compute_move_and_state",
        string="Selling Move",
        readonly=True,
        store=True,
    )
    sell_state = fields.Selection(
        related="sell_move_id.state", string="Sell Move State", readonly=True
    )
    sell_picking_id = fields.Many2one(
        "stock.picking",
        related="sell_move_id.picking_id",
        string="Sell Delivery Order",
        readonly=True,
    )
    end_date = fields.Date(
        compute="_compute_end_date",
        string="End Date",
        store=True,
        help="End Date of the Rental (extensions included), \
        taking into account all the extensions sold to the customer.",
    )
    state = fields.Selection(
        [
            ("ordered", "Ordered"),
            ("out", "Out"),
            ("sell_progress", "Sell in progress"),
            ("sold", "Sold"),
            ("in", "Back In"),
            ("cancel", "Cancelled"),
        ],
        string="State",
        compute="_compute_move_and_state",
        readonly=True,
        store=True,
    )
