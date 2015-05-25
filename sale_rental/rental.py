# -*- encoding: utf-8 -*-
##############################################################################
#
#    Sale Rental module for Odoo
#    Copyright (C) 2014-2015 Akretion (http://www.akretion.com)
#    @author Alexis de Lattre <alexis.delattre@akretion.com>
#
#    This program is free software: you can redistribute it and/or modify
#    it under the terms of the GNU Affero General Public License as
#    published by the Free Software Foundation, either version 3 of the
#    License, or (at your option) any later version.
#
#    This program is distributed in the hope that it will be useful,
#    but WITHOUT ANY WARRANTY; without even the implied warranty of
#    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#    GNU Affero General Public License for more details.
#
#    You should have received a copy of the GNU Affero General Public License
#    along with this program.  If not, see <http://www.gnu.org/licenses/>.
#
##############################################################################

from openerp import models, fields, api, _
from openerp.exceptions import Warning, ValidationError
from openerp.tools import float_compare
from dateutil.relativedelta import relativedelta
import openerp.addons.decimal_precision as dp
import logging

logger = logging.getLogger(__name__)
# TODO : block if we sell a rented product already sold => state


class ProductProduct(models.Model):
    _inherit = 'product.product'

    # Link rental service -> rented HW product
    rented_product_id = fields.Many2one(
        'product.product', string='Related Rented Product',
        domain=[('type', 'in', ('product', 'consu'))])
    # Link rented HW product -> rental service
    rental_service_ids = fields.One2many(
        'product.product', 'rented_product_id',
        string='Related Rental Services')

    @api.one
    @api.constrains('rented_product_id', 'must_have_dates')
    def _check_rental(self):
        if self.rented_product_id and self.type != 'service':
            raise ValidationError(
                _("The rental product '%s' must be of type 'Service'.")
                % self.name)
        if self.rented_product_id and not self.must_have_dates:
            raise ValidationError(
                _("The rental product '%s' must have the option "
                    "''Must Have Start and End Dates' checked.")
                % self.name)
        # In the future, we would like to support all time UoMs
        # but it is more complex and requires additionnal developments
        day_uom = self.env.ref('product.product_uom_day')
        if self.rented_product_id and self.uom_id != day_uom:
            raise ValidationError(
                _("The unit of measure of the rental product '%s' must "
                    "be 'Day'.")
                % self.name)


class SaleOrder(models.Model):
    _inherit = 'sale.order'

    @api.model
    def _get_rental_date_planned(self, line):
        return line.start_date

    @api.model
    def _prepare_order_line_procurement(
            self, order, line, group_id=False):
        res = super(SaleOrder, self)._prepare_order_line_procurement(
            order, line, group_id=group_id)
        if (
                line.product_id.rented_product_id
                and line.rental_type == 'new_rental'):
            res.update({
                'product_id': line.product_id.rented_product_id.id,
                'product_qty': line.rental_qty,
                'product_uos_qty': line.rental_qty,
                'product_uom': line.product_id.rented_product_id.uom_id.id,
                'product_uos': line.product_id.rented_product_id.uom_id.id,
                'location_id':
                order.warehouse_id.rental_out_location_id.id,
                'route_ids':
                [(6, 0, [line.order_id.warehouse_id.rental_route_id.id])],
                'date_planned': self._get_rental_date_planned(line),
                })
        elif line.sell_rental_id:
            res['route_ids'] = [(6, 0, [
                line.order_id.warehouse_id.sell_rented_product_route_id.id])]
        return res

    @api.model
    def _prepare_rental(self, so_line):
        return {'start_order_line_id': so_line.id}

    @api.multi
    def action_button_confirm(self):
        res = super(SaleOrder, self).action_button_confirm()
        for order in self:
            for line in order.order_line:
                if line.rental_type == 'new_rental':
                    self.env['sale.rental'].create(self._prepare_rental(line))
                elif line.rental_type == 'rental_extension':
                    line.extension_rental_id.in_move_id.date_expected =\
                        line.end_date
                    line.extension_rental_id.in_move_id.date = line.end_date
                elif line.sell_rental_id:
                    if line.sell_rental_id.out_move_id.state != 'done':
                        raise Warning(
                            _('Cannot sell the rental %s because it has '
                                'not been delivered')
                            % line.sell_rental_id.display_name)
                    line.sell_rental_id.in_move_id.action_cancel()
        return res


class SaleOrderLine(models.Model):
    _inherit = 'sale.order.line'

    rental = fields.Boolean(string='Rental')
    can_sell_rental = fields.Boolean(string='Can Sell from Rental')
    rental_type = fields.Selection([
        ('new_rental', 'New Rental'),
        ('rental_extension', 'Rental Extension'),
        ], 'Rental Type',
        readonly=True, states={'draft': [('readonly', False)]})
    extension_rental_id = fields.Many2one(
        'sale.rental', string='Rental to Extend')
    rental_qty = fields.Float(
        string='Rental Quantity', digits=dp.get_precision('Product UoS'))
    sell_rental_id = fields.Many2one(
        'sale.rental', string='Rental to Sell')

    @api.one
    @api.constrains(
        'rental_type', 'extension_rental_id', 'start_date', 'end_date',
        'rental_qty', 'product_uom_qty', 'product_id', 'must_have_dates')
    def _check_sale_line_rental(self):
        if self.rental_type == 'rental_extension':
            if not self.extension_rental_id:
                raise ValidationError(
                    _("Missing Rental to Extend on the sale order line with "
                        "rental service %s")
                    % self.product_id.name)
            if self.rental_qty != self.extension_rental_id.rental_qty:
                raise ValidationError(
                    _("On the sale order line with rental service %s, "
                        "you are trying to extend a rental with a rental "
                        "quantity (%s) that is different from the quantity "
                        "of the original rental (%s). This is not supported.")
                    % (
                        self.product_id.name,
                        self.rental_qty,
                        self.extension_rental_id.rental_qty))
        if self.rental_type in ('new_rental', 'rental_extension'):
            if not self.product_id.rented_product_id:
                raise ValidationError(
                    _("On the 'new rental' sale order line with product '%s', "
                        "we should have a rental service product !") % (
                        self.product_id.name))
            if self.product_uom_qty != self.rental_qty * self.number_of_days:
                raise ValidationError(
                    _("On the sale order line with product '%s' "
                        "the Product Quantity (%s) should be the "
                        "number of days (%s) "
                        "multiplied by the Rental Quantity (%s).") % (
                        self.product_id.name, self.product_uom_qty,
                        self.number_of_days, self.rental_qty))
            if not self.must_have_dates:
                raise ValidationError(
                    _("On the rental sale order line with product %s"
                        "the must have dates option should be enabled")
                    % self.product_id.name)
                # the module sale_start_end_dates checks that, when we have
                # must_have_dates, we have start + end dates
        elif self.sell_rental_id:
            if self.product_uom_qty != self.sell_rental_id.rental_qty:
                raise ValidationError(
                    _("On the sale order line with product %s "
                        "you are trying to sell a rented product with a "
                        "quantity (%s) that is different from the rented "
                        "quantity (%s). This is not supported.") % (
                        self.product_id.name,
                        self.product_uom_qty,
                        self.sell_rental_id.rental_qty))

    @api.multi
    def need_procurement(self):
        res = super(SaleOrderLine, self).need_procurement()
        if not res:
            for soline in self:
                if (
                        soline.product_id.rented_product_id
                        and soline.rental_type == 'new_rental'):
                    return True
        return res

    @api.multi
    def product_id_change_with_wh(
            self, pricelist, product, qty=0,
            uom=False, qty_uos=0, uos=False, name='', partner_id=False,
            lang=False, update_tax=True, date_order=False, packaging=False,
            fiscal_position=False, flag=False, warehouse_id=False):
        res = super(SaleOrderLine, self).product_id_change_with_wh(
            pricelist, product, qty=qty, uom=uom,
            qty_uos=qty_uos, uos=uos, name=name, partner_id=partner_id,
            lang=lang, update_tax=update_tax, date_order=date_order,
            packaging=packaging, fiscal_position=fiscal_position,
            flag=flag, warehouse_id=warehouse_id)
        if not product:
            res['value'].update({
                'rental_type': False,
                'rental': False,
                'rental_qty': 0,
                'can_sell_rental': False,
                'sell_rental_id': False,
                })
        else:
            product_o = self.env['product.product'].browse(product)
            if product_o.rented_product_id:
                res['value']['rental'] = True
                # We can't set rental_type to default value 'new_rental' here
                # because we would need to check if rental_type is False
                # and we don't have rental_type as arg of
                # product_id_change_with_wh()
            else:
                res['value'].update({
                    'rental_type': False,
                    'rental': False,
                    'rental_qty': 0,
                    })
            if product_o.rental_service_ids:
                res['value']['can_sell_rental'] = True
            else:
                res['value'].update({
                    'can_sell_rental': False,
                    'sell_rental_id': False,
                    })
        return res

    @api.multi
    def product_uom_qty_change_with_wh_with_rental(
            self, pricelist, product, qty=0,
            uom=False, qty_uos=0, uos=False, name='', partner_id=False,
            lang=False, update_tax=True, date_order=False, packaging=False,
            fiscal_position=False, flag=False, warehouse_id=False,
            rental_type=False, rental_qty=0):
        res = super(SaleOrderLine, self).product_id_change_with_wh(
            pricelist, product, qty=qty, uom=uom,
            qty_uos=qty_uos, uos=uos, name=name, partner_id=partner_id,
            lang=lang, update_tax=update_tax, date_order=date_order,
            packaging=packaging, fiscal_position=fiscal_position,
            flag=flag, warehouse_id=warehouse_id)
        if (
                product
                and rental_type == 'new_rental'
                and rental_qty
                and warehouse_id):
            product_o = self.env['product.product'].browse(product)
            if product_o.rented_product_id:
                product_uom = product_o.rented_product_id.uom_id
                warehouse = self.env['stock.warehouse'].browse(warehouse_id)
                rental_in_location = warehouse.rental_in_location_id
                product_o_in = self.with_context(
                    location=rental_in_location.id).env['product.product']\
                    .browse(product)
                in_location_available_qty =\
                    product_o_in.rented_product_id.qty_available\
                    - product_o_in.rented_product_id.outgoing_qty
                compare_qty = float_compare(
                    in_location_available_qty,
                    rental_qty, precision_rounding=product_uom.rounding)
                if compare_qty == -1:
                    res['warning'] = {
                        'title': _("Not enough stock !"),
                        'message':
                        _("You want to rent %.2f %s but you only "
                            "have %.2f %s currently available on the stock "
                            "location '%s' ! Make sure that you get some "
                            "units back in the mean time or re-supply the "
                            "stock location '%s'.")
                        % (rental_qty, product_uom.name,
                            in_location_available_qty,
                            product_uom.name, rental_in_location.name,
                            rental_in_location.name)
                    }
        return res

    @api.onchange('extension_rental_id')
    def extension_rental_id_change(self):
        if (
                self.product_id
                and self.rental_type == 'rental_extension'
                and self.extension_rental_id):
            if self.extension_rental_id.rental_product_id != self.product_id:
                raise Warning(
                    _("The Rental Service of the Rental Extension you just "
                        "selected is '%s' and it's not the same as the "
                        "Product currently selected in this Sale Order Line.")
                    % self.extension_rental_id.rental_product_id.name)
            initial_end_date = fields.Date.from_string(
                self.extension_rental_id.end_date)
            self.start_date = initial_end_date + relativedelta(days=1)
            self.rental_qty = self.extension_rental_id.rental_qty

    @api.onchange('sell_rental_id')
    def sell_rental_id_change(self):
        if self.sell_rental_id:
            self.product_uom_qty = self.sell_rental_id.rental_qty
            self.product_uos_qty = self.sell_rental_id.rental_qty

    @api.onchange('rental_qty', 'number_of_days')
    def rental_qty_number_of_days_change(self):
        qty = self.rental_qty * self.number_of_days
        self.product_uom_qty = qty
        self.product_uos_qty = qty


class SaleRental(models.Model):
    _name = 'sale.rental'
    _description = "Rental"
    _order = "id desc"
    _rec_name = "display_name"

    @api.one
    @api.depends(
        'start_order_line_id', 'extension_order_line_ids.end_date',
        'extension_order_line_ids.state', 'start_order_line_id.end_date')
    def _display_name(self):
        self.display_name = u'[%s] %s - %s > %s (%s)' % (
            self.partner_id.name,
            self.rented_product_id.name,
            self.start_date,
            self.end_date,
            self.state)  # TODO : display label, not the technical key

    @api.one
    @api.depends('start_order_line_id', 'start_order_line_id.procurement_ids')
    def _compute_procurement_and_move(self):
        procurement = False
        in_move = False
        out_move = False
        sell_procurement = False
        sell_move = False
        state = False
        if (
                self.start_order_line_id
                and self.start_order_line_id.procurement_ids):

            procurement = self.start_order_line_id.procurement_ids[0]
            if procurement.move_ids:
                for move in procurement.move_ids:
                    if move.move_dest_id:
                        out_move = move
                    else:
                        in_move = move
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
                        out_move.state == 'done'
                        and in_move.state == 'cancel'
                        and sell_procurement):
                    state = 'sell_progress'
                    if sell_move and sell_move.state == 'done':
                        state = 'sold'
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
        compute='_display_name', string='Display Name')
    start_order_line_id = fields.Many2one(
        'sale.order.line', string='Rental Sale Order Line')
    start_date = fields.Date(
        related='start_order_line_id.start_date',
        string='Start Date', readonly=True)
    rental_product_id = fields.Many2one(
        'product.product', related='start_order_line_id.product_id',
        string="Rental Service", readonly=True)
    rented_product_id = fields.Many2one(
        'product.product',
        related='start_order_line_id.product_id.rented_product_id',
        string="Rented Product", readonly=True)
    rental_qty = fields.Float(
        related='start_order_line_id.rental_qty',
        string="Rental Quantity", readonly=True)
    start_order_id = fields.Many2one(
        'sale.order', related='start_order_line_id.order_id',
        string='Rental Sale Order', readonly=True)
    company_id = fields.Many2one(
        'res.company', related='start_order_id.company_id',
        string='Company', readonly=True)
    partner_id = fields.Many2one(
        'res.partner', related='start_order_id.partner_id',
        string='Partner', readonly=True)
    procurement_id = fields.Many2one(
        'procurement.order', string="Procurement", readonly=True,
        compute='_compute_procurement_and_move')
    out_move_id = fields.Many2one(
        'stock.move', compute='_compute_procurement_and_move',
        string='Outgoing Stock Move', readonly=True)
    in_move_id = fields.Many2one(
        'stock.move', compute='_compute_procurement_and_move',
        string='Return Stock Move', readonly=True)
    out_state = fields.Selection([
        ('draft', 'New'),
        ('cancel', 'Cancelled'),
        ('waiting', 'Waiting Another Move'),
        ('confirmed', 'Waiting Availability'),
        ('assigned', 'Available'),
        ('done', 'Done'),
        ], readonly=True, related='out_move_id.state',
        string='State of the Outgoing Stock Move')
    in_state = fields.Selection([
        ('draft', 'New'),
        ('cancel', 'Cancelled'),
        ('waiting', 'Waiting Another Move'),
        ('confirmed', 'Waiting Availability'),
        ('assigned', 'Available'),
        ('done', 'Done'),
        ], readonly=True, related='in_move_id.state',
        string='State of the Return Stock Move')
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
        compute='_compute_procurement_and_move')
    sell_move_id = fields.Many2one(
        'stock.move', compute='_compute_procurement_and_move',
        string='Sell Stock Move', readonly=True)
    sell_state = fields.Selection([
        ('draft', 'New'),
        ('cancel', 'Cancelled'),
        ('waiting', 'Waiting Another Move'),
        ('confirmed', 'Waiting Availability'),
        ('assigned', 'Available'),
        ('done', 'Done'),
        ], readonly=True, related='sell_move_id.state',
        string='State of the Sell Stock Move')
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
        ], string='State', compute='_compute_procurement_and_move',
        readonly=True)


class StockWarehouse(models.Model):
    _inherit = "stock.warehouse"

    rental_in_location_id = fields.Many2one(
        'stock.location', 'Rental In', domain=[('usage', '<>', 'view')])
    rental_out_location_id = fields.Many2one(
        'stock.location', 'Rental Out', domain=[('usage', '<>', 'view')])
    rental_allowed = fields.Boolean('Rental Allowed', default=True)
    rental_route_id = fields.Many2one(
        'stock.location.route', string='Rental Route')
    sell_rented_product_route_id = fields.Many2one(
        'stock.location.route', string='Sell Rented Product Route')

    @api.multi
    def _get_rental_push_pull_rules(self):
        self.ensure_one()
        route_obj = self.env['stock.location.route']
        try:
            rental_route = self.env.ref('sale_rental.route_warehouse0_rental')
        except:
            rental_routes = route_obj.search([('name', '=', _('Rent'))])
            rental_route = rental_routes and rental_routes[0] or False
        if not rental_route:
            raise Warning(_("Can't find any generic 'Rent' route."))
        try:
            sell_rented_product_route = self.env.ref(
                'sale_rental.route_warehouse0_sell_rented_product')
        except:
            sell_rented_product_routes = route_obj.search(
                [('name', '=', _('Sell Rented Product'))])
            sell_rented_product_route =\
                sell_rented_product_routes and sell_rented_product_routes[0]\
                or False
        if not sell_rented_product_route:
            raise Warning(
                _("Can't find any generic 'Sell Rented Product' route."))

        if not self.rental_in_location_id:
            raise Warning(
                _("The Rental Input stock location is not set on the "
                    "warehouse %s") % self.name)
        if not self.rental_out_location_id:
            raise Warning(
                _("The Rental Output stock location is not set on the "
                    "warehouse %s") % self.name)
        rental_pull_rule = {
            'name': self.pool['stock.warehouse']._format_rulename(
                self._cr, self._uid, self, self.rental_in_location_id,
                self.rental_out_location_id, self.env.context),
            'location_id': self.rental_out_location_id.id,
            'location_src_id': self.rental_in_location_id.id,
            'route_id': rental_route.id,
            'action': 'move',
            'picking_type_id': self.out_type_id.id,
            'warehouse_id': self.id,
        }
        rental_push_rule = {
            'name': self.pool['stock.warehouse']._format_rulename(
                self._cr, self._uid, self, self.rental_out_location_id,
                self.rental_in_location_id, self.env.context),
            'location_from_id': self.rental_out_location_id.id,
            'location_dest_id': self.rental_in_location_id.id,
            'route_id': rental_route.id,
            'auto': 'auto',
            'invoice_state': 'none',
            'picking_type_id': self.in_type_id.id,
            'warehouse_id': self.id,
            }
        sell_rented_product_pull_rule = {
            'name': self.pool['stock.warehouse']._format_rulename(
                self._cr, self._uid, self, self.rental_out_location_id,
                self.out_type_id.default_location_dest_id, self.env.context),
            'location_id': self.out_type_id.default_location_dest_id.id,
            'location_src_id': self.rental_out_location_id.id,
            'route_id': sell_rented_product_route.id,
            'action': 'move',
            'picking_type_id': self.out_type_id.id,
            'warehouse_id': self.id,
            }
        return {
            'procurement.rule': [
                rental_pull_rule,
                sell_rented_product_pull_rule],
            'stock.location.path': [rental_push_rule],
            }

    @api.multi
    def write(self, vals):
        if 'rental_allowed' in vals:
            if vals.get('rental_allowed'):
                for warehouse in self:
                    for obj, rules_list in\
                            self._get_rental_push_pull_rules().iteritems():
                        for rule in rules_list:
                            self.env[obj].create(rule)
            else:
                for warehouse in self:
                    warehouse.rental_route_id.pull_ids.unlink()
                    warehouse.rental_route_id.push_ids.unlink()
                    warehouse.sell_rented_product_route_id.pull_ids.unlink()
                    warehouse.sell_rented_product_route_id.push_ids.unlink()
        return super(StockWarehouse, self).write(vals)


class StockMove(models.Model):
    _inherit = 'stock.move'

    @api.model
    def _create_invoice_line_from_vals(self, move, invoice_line_vals):
        '''When we invoice from delivery, we shouldn't invoice
        the rented product'''
        if (
                move.procurement_id
                and move.procurement_id.sale_line_id
                and move.procurement_id.sale_line_id.rental):
            return False
        else:
            return super(StockMove, self)._create_invoice_line_from_vals(
                move, invoice_line_vals)


class StockLocationPath(models.Model):
    _inherit = 'stock.location.path'

    @api.model
    def _prepare_push_apply(self, rule, move):
        '''Inherit to write the end date of the rental on the return move'''
        vals = super(StockLocationPath, self)._prepare_push_apply(rule, move)
        if (
                move.procurement_id
                and move.procurement_id.location_id ==
                move.procurement_id.warehouse_id.rental_out_location_id
                and move.procurement_id.sale_line_id
                and move.procurement_id.sale_line_id
                .rental_type == 'new_rental'):
            rental_end_date = move.procurement_id.sale_line_id.end_date
            vals['date'] = vals['date_expected'] = rental_end_date
        return vals
