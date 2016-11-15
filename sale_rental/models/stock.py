# -*- coding: utf-8 -*-
# Copyright 2014-2016 Akretion (http://www.akretion.com)
# @author Alexis de Lattre <alexis.delattre@akretion.com>
# Copyright 2016 Sodexis (http://sodexis.com)
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from openerp import models, fields, api, _
from openerp.exceptions import UserError
import logging

logger = logging.getLogger(__name__)


class StockWarehouse(models.Model):
    _inherit = "stock.warehouse"

    rental_view_location_id = fields.Many2one(
        'stock.location', 'Parent Rental', domain=[('usage', '=', 'view')])
    rental_in_location_id = fields.Many2one(
        'stock.location', 'Rental In', domain=[('usage', '!=', 'view')])
    rental_out_location_id = fields.Many2one(
        'stock.location', 'Rental Out', domain=[('usage', '!=', 'view')])
    rental_allowed = fields.Boolean('Rental Allowed')
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
            raise UserError(_("Can't find any generic 'Rent' route."))
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
            raise UserError(_(
                "Can't find any generic 'Sell Rented Product' route."))

        if not self.rental_in_location_id:
            raise UserError(_(
                "The Rental Input stock location is not set on the "
                "warehouse %s") % self.name)
        if not self.rental_out_location_id:
            raise UserError(_(
                "The Rental Output stock location is not set on the "
                "warehouse %s") % self.name)
        rental_pull_rule = {
            'name': self.env['stock.warehouse']._format_rulename(
                self, self.rental_in_location_id,
                self.rental_out_location_id),
            'location_id': self.rental_out_location_id.id,
            'location_src_id': self.rental_in_location_id.id,
            'route_id': rental_route.id,
            'action': 'move',
            'picking_type_id': self.out_type_id.id,
            'warehouse_id': self.id,
        }
        rental_push_rule = {
            'name': self.env['stock.warehouse']._format_rulename(
                self, self.rental_out_location_id,
                self.rental_in_location_id),
            'location_from_id': self.rental_out_location_id.id,
            'location_dest_id': self.rental_in_location_id.id,
            'route_id': rental_route.id,
            'picking_type_id': self.in_type_id.id,
            'warehouse_id': self.id,
            }
        customer_loc = self.env.ref('stock.stock_location_customers')
        sell_rented_product_pull_rule = {
            'name': self.env['stock.warehouse']._format_rulename(
                self, self.rental_out_location_id, customer_loc),
            'location_id': customer_loc.id,
            'location_src_id': self.rental_out_location_id.id,
            'route_id': sell_rented_product_route.id,
            'action': 'move',
            'picking_type_id': self.out_type_id.id,
            'warehouse_id': self.id,
            }
        res = {
            'procurement.rule': [
                rental_pull_rule,
                sell_rented_product_pull_rule],
            'stock.location.path': [rental_push_rule],
            }
        return res

    @api.multi
    def write(self, vals):
        if 'rental_allowed' in vals:
            rental_route = self.env.ref('sale_rental.route_warehouse0_rental')
            sell_rented_route = self.env.ref(
                'sale_rental.route_warehouse0_sell_rented_product')
            if vals.get('rental_allowed'):
                for warehouse in self:
                    # create stock locations
                    slo = self.env['stock.location']
                    if not warehouse.rental_view_location_id:
                        view_loc = slo.create({
                            'name': _('Rental'),
                            'location_id': self.view_location_id.id,
                            'usage': 'view',
                            })
                        logger.debug(
                            'New view rental stock location created ID %d',
                            view_loc.id)
                        warehouse.rental_view_location_id = view_loc.id
                    if not warehouse.rental_in_location_id:
                        in_loc = slo.create({
                            'name': _('Rental In'),
                            'location_id':
                            warehouse.rental_view_location_id.id,
                            })
                        logger.debug(
                            'New in rental stock location created ID %d',
                            in_loc.id)
                        warehouse.rental_in_location_id = in_loc.id
                    if not warehouse.rental_out_location_id:
                        out_loc = slo.create({
                            'name': _('Rental Out'),
                            'location_id':
                            warehouse.rental_view_location_id.id,
                            })
                        logger.debug(
                            'New out rental stock location created ID %d',
                            out_loc.id)
                        warehouse.rental_out_location_id = out_loc.id
                    warehouse.write({
                        'route_ids': [(4, rental_route.id)],
                        'rental_route_id': rental_route.id,
                        'sell_rented_product_route_id': sell_rented_route.id,
                        })
                    for obj, rules_list in\
                            self._get_rental_push_pull_rules().iteritems():
                        for rule in rules_list:
                            self.env[obj].create(rule)
            else:
                for warehouse in self:
                    pull_rules_to_delete = self.env['procurement.rule'].search(
                        [
                            ('route_id', 'in', (
                                warehouse.rental_route_id.id,
                                warehouse.sell_rented_product_route_id.id)),
                            ('location_src_id', 'in', (
                                warehouse.rental_out_location_id.id,
                                warehouse.rental_in_location_id.id)),
                            ('action', '=', 'move')])
                    pull_rules_to_delete.unlink()
                    push_rule_to_delete =\
                        self.env['stock.location.path'].search([
                            ('route_id', '=', warehouse.rental_route_id.id),
                            ('location_from_id', '=',
                                warehouse.rental_out_location_id.id),
                            ('location_dest_id', '=',
                                warehouse.rental_in_location_id.id)])
                    push_rule_to_delete.unlink()
                    warehouse.write({
                        'route_ids': [(3, rental_route.id)],
                        'rental_route_id': False,
                        'sell_rented_product_route_id': False,
                        })
        return super(StockWarehouse, self).write(vals)


class StockLocationPath(models.Model):
    _inherit = 'stock.location.path'

    @api.model
    def _prepare_push_apply(self, rule, move):
        '''Inherit to write the end date of the rental on the return move'''
        vals = super(StockLocationPath, self)._prepare_push_apply(rule, move)
        if (
                move.procurement_id and
                move.procurement_id.location_id ==
                move.procurement_id.warehouse_id.rental_out_location_id and
                move.procurement_id.sale_line_id and
                move.procurement_id.sale_line_id.rental_type == 'new_rental'):
            rental_end_date = move.procurement_id.sale_line_id.end_date
            vals['date'] = vals['date_expected'] = rental_end_date
        return vals


class StockInventory(models.Model):
    _inherit = 'stock.inventory'

    @api.multi
    def create_demo_and_validate(self):
        silo = self.env['stock.inventory.line']
        demo_inv = self.env.ref('sale_rental.rental_inventory')
        rental_in_loc = self.env.ref('stock.warehouse0').rental_in_location_id
        products = [
            ('product.product_product_6', 56),
            ('product.product_product_8', 46),
            ('product.product_product_25', 2),
            ]
        for (product_xmlid, qty) in products:
            product = self.env.ref(product_xmlid)
            silo.create({
                'product_id': product.id,
                'product_uom_id': product.uom_id.id,
                'inventory_id': demo_inv.id,
                'product_qty': qty,
                'location_id': rental_in_loc.id,
            })
        demo_inv.action_done()
        return True
