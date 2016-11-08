# -*- coding: utf-8 -*-
# © 2014-2016 Akretion (http://www.akretion.com)
# @author Alexis de Lattre <alexis.delattre@akretion.com>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from openerp import models, fields, api
import logging

logger = logging.getLogger(__name__)
# TODO : block if we sell a rented product already sold => state


class SaleRental(models.Model):
    _name = 'sale.rental'
    _description = "Rental"
    _order = "id desc"
    _rec_name = "display_name"

    @api.one
    @api.depends(
        'start_order_line_id', 'extension_order_line_ids.end_date',
        'extension_order_line_ids.state', 'start_order_line_id.end_date')
    def _compute_display_name_field(self):
        self.display_name = u'[%s] %s - %s > %s (%s)' % (
            self.partner_id.name,
            self.rented_product_id.name,
            self.start_date,
            self.end_date,
            self._fields['state'].convert_to_export(self.state, self.env))

    @api.one
    @api.depends(
        'start_order_line_id.order_id.state',
        'start_order_line_id.procurement_ids.move_ids.state',
        'start_order_line_id.procurement_ids.move_ids.move_dest_id.state',
        'sell_order_line_ids.procurement_ids.move_ids.state',
        )
    def _compute_procurement_and_move(self):
        procurement = False
        in_move = False
        out_move = False
        sell_procurement = False
        sell_move = False
        state = False
        if (
                self.start_order_line_id and
                self.start_order_line_id.procurement_ids):

            procurement = self.start_order_line_id.procurement_ids[0]
            if procurement.move_ids:
                for move in procurement.move_ids:
                    if move.move_dest_id:
                        out_move = move
                        in_move = move.move_dest_id
            if (
                    self.sell_order_line_ids and
                    self.sell_order_line_ids[0].procurement_ids):
                sell_procurement =\
                    self.sell_order_line_ids[0].procurement_ids[0]
                if sell_procurement.move_ids:
                    sell_move = sell_procurement.move_ids[0]
            state = 'ordered'
            if out_move and in_move:
                if out_move.state == 'done':
                    state = 'out'
                if out_move.state == 'done' and in_move.state == 'done':
                    state = 'in'
                if (
                        out_move.state == 'done' and
                        in_move.state == 'cancel' and
                        sell_procurement):
                    state = 'sell_progress'
                    if sell_move and sell_move.state == 'done':
                        state = 'sold'
            if self.start_order_line_id.order_id.state == 'cancel':
                state = 'cancel'
        self.procurement_id = procurement
        self.in_move_id = in_move
        self.out_move_id = out_move
        self.state = state
        self.sell_procurement_id = sell_procurement
        self.sell_move_id = sell_move

    @api.one
    @api.depends(
        'extension_order_line_ids.end_date', 'extension_order_line_ids.state',
        'start_order_line_id.end_date')
    def _compute_end_date(self):
        end_date = False
        if self.extension_order_line_ids:
            for extension in self.extension_order_line_ids:
                if extension.state not in ('cancel', 'draft'):
                    if extension.end_date > end_date:
                        end_date = extension.end_date
        if not end_date and self.start_order_line_id:
            end_date = self.start_order_line_id.end_date
        self.end_date = end_date

    display_name = fields.Char(
        compute='_compute_display_name_field', string='Display Name',
        readonly=True)
    start_order_line_id = fields.Many2one(
        'sale.order.line', string='Rental Sale Order Line', readonly=True)
    start_date = fields.Date(
        related='start_order_line_id.start_date', readonly=True, store=True)
    rental_product_id = fields.Many2one(
        'product.product', related='start_order_line_id.product_id',
        string="Rental Service", readonly=True)
    rented_product_id = fields.Many2one(
        'product.product',
        related='start_order_line_id.product_id.rented_product_id',
        string="Rented Product", readonly=True)
    rental_qty = fields.Float(
        related='start_order_line_id.rental_qty', readonly=True)
    start_order_id = fields.Many2one(
        'sale.order', related='start_order_line_id.order_id',
        string='Rental Sale Order', readonly=True)
    company_id = fields.Many2one(
        'res.company', related='start_order_line_id.order_id.company_id',
        string='Company', readonly=True)
    partner_id = fields.Many2one(
        'res.partner', related='start_order_line_id.order_id.partner_id',
        string='Customer', readonly=True, store=True)
    procurement_id = fields.Many2one(
        'procurement.order', string="Procurement", readonly=True,
        compute='_compute_procurement_and_move', store=True)
    out_move_id = fields.Many2one(
        'stock.move', compute='_compute_procurement_and_move',
        string='Outgoing Stock Move', readonly=True, store=True)
    in_move_id = fields.Many2one(
        'stock.move', compute='_compute_procurement_and_move',
        string='Return Stock Move', readonly=True, store=True)
    out_state = fields.Selection(
        related='out_move_id.state',
        string='State of the Outgoing Stock Move', readonly=True)
    in_state = fields.Selection(
        related='in_move_id.state',
        string='State of the Return Stock Move', readonly=True)
    out_picking_id = fields.Many2one(
        'stock.picking', related='out_move_id.picking_id',
        string='Delivery Order', readonly=True)
    in_picking_id = fields.Many2one(
        'stock.picking', related='in_move_id.picking_id',
        string='Return Picking', readonly=True)
    extension_order_line_ids = fields.One2many(
        'sale.order.line', 'extension_rental_id',
        string='Rental Extensions', readonly=True)
    sell_order_line_ids = fields.One2many(
        'sale.order.line', 'sell_rental_id',
        string='Sell Rented Product', readonly=True)
    sell_procurement_id = fields.Many2one(
        'procurement.order', string="Sell Procurement", readonly=True,
        compute='_compute_procurement_and_move', store=True)
    sell_move_id = fields.Many2one(
        'stock.move', compute='_compute_procurement_and_move',
        string='Sell Stock Move', readonly=True, store=True)
    sell_state = fields.Selection(
        related='sell_move_id.state',
        string='State of the Sell Stock Move', readonly=True)
    sell_picking_id = fields.Many2one(
        'stock.picking', related='sell_move_id.picking_id',
        string='Sell Delivery Order', readonly=True)
    end_date = fields.Date(
        compute='_compute_end_date', string='End Date (extensions included)',
        readonly=True,
        help="End Date of the Rental, taking into account all the "
        "extensions sold to the customer.")
    state = fields.Selection([
        ('ordered', 'Ordered'),
        ('out', 'Out'),
        ('sell_progress', 'Sell in progress'),
        ('sold', 'Sold'),
        ('in', 'Back In'),
        ('cancel', 'Cancelled'),
        ], string='State', compute='_compute_procurement_and_move',
        readonly=True, store=True)
