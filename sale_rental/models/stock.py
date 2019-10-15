# Copyright 2014-2019 Akretion France (http://www.akretion.com)
# @author Alexis de Lattre <alexis.delattre@akretion.com>
# Copyright 2016-2019 Sodexis (http://sodexis.com)
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo import api, fields, models, _
from odoo.exceptions import UserError
import logging

logger = logging.getLogger(__name__)


class StockWarehouse(models.Model):
    _inherit = "stock.warehouse"

    rental_view_location_id = fields.Many2one(
        'stock.location', 'Parent Rental', domain=[('usage', '=', 'view')])
    rental_in_location_id = fields.Many2one(
        'stock.location', 'Rental In', domain=[('usage', '=', 'internal')])
    rental_out_location_id = fields.Many2one(
        'stock.location', 'Rental Out', domain=[('usage', '!=', 'view')])
    rental_allowed = fields.Boolean('Rental Allowed')
    rental_route_id = fields.Many2one(
        'stock.location.route', string='Rental Route')
    sell_rented_product_route_id = fields.Many2one(
        'stock.location.route', string='Sell Rented Product Route')

    @api.onchange('rental_allowed')
    def _onchange_rental_allowed(self):
        if not self.rental_allowed:
            self.rental_view_location_id = False
            self.rental_in_location_id = False
            self.rental_out_location_id = False
            self.rental_route_id = False
            self.sell_rented_product_route_id = False

    def _get_rental_push_pull_rules(self):
        self.ensure_one()
        route_obj = self.env['stock.location.route']
        try:
            rental_route = self.env.ref('sale_rental.route_warehouse0_rental')
        except Exception:
            rental_routes = route_obj.search([('name', '=', _('Rent'))])
            rental_route = rental_routes and rental_routes[0] or False
        if not rental_route:
            raise UserError(_("Can't find any generic 'Rent' route."))
        try:
            sell_rented_product_route = self.env.ref(
                'sale_rental.route_warehouse0_sell_rented_product')
        except Exception:
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
            'name': self._format_rulename(
                self.rental_in_location_id,
                self.rental_out_location_id, ''),
            'location_src_id': self.rental_in_location_id.id,
            'location_id': self.rental_out_location_id.id,
            'route_id': rental_route.id,
            'action': 'pull',
            'picking_type_id': self.out_type_id.id,
            'warehouse_id': self.id,
        }
        rental_push_rule = {
            'name': self._format_rulename(
                self.rental_out_location_id,
                self.rental_in_location_id, ''),
            'location_src_id': self.rental_out_location_id.id,
            'location_id': self.rental_in_location_id.id,
            'route_id': rental_route.id,
            'action': 'push',
            'picking_type_id': self.in_type_id.id,
            'warehouse_id': self.id,
        }
        customer_loc = self.env.ref('stock.stock_location_customers')
        sell_rented_product_pull_rule = {
            'name': self._format_rulename(
                self.rental_out_location_id, customer_loc, ''),
            'location_src_id': self.rental_out_location_id.id,
            'location_id': customer_loc.id,
            'route_id': sell_rented_product_route.id,
            'action': 'pull',
            'picking_type_id': self.out_type_id.id,
            'warehouse_id': self.id,
        }
        res = [
            rental_pull_rule,
            rental_push_rule,
            sell_rented_product_pull_rule,
            ]
        return res

    def _create_rental_locations(self):
        slo = self.env['stock.location']
        for wh in self:
            # create stock locations
            if not wh.rental_view_location_id:
                view_loc = slo.with_context(lang='en_US').search([
                    ('name', 'ilike', 'Rental'),
                    ('location_id', '=', wh.view_location_id.id),
                    ('usage', '=', 'view')], limit=1)
                if not view_loc:
                    view_loc = slo.with_context(lang='en_US').create({
                        'name': 'Rental',
                        'location_id': wh.view_location_id.id,
                        'usage': 'view',
                    })
                    slo.browse(view_loc.id).name = _('Rental')
                    logger.debug(
                        'New view rental stock location created ID %d',
                        view_loc.id)
                wh.rental_view_location_id = view_loc.id
            if not wh.rental_in_location_id:
                in_loc = slo.with_context(lang='en_US').search([
                    ('name', 'ilike', 'Rental In'),
                    ('location_id', '=', wh.rental_view_location_id.id),
                    ], limit=1)
                if not in_loc:
                    in_loc = slo.with_context(lang='en_US').create({
                        'name': 'Rental In',
                        'location_id': wh.rental_view_location_id.id,
                        })
                    slo.browse(in_loc.id).name = _('Rental In')
                    logger.debug(
                        'New in rental stock location created ID %d',
                        in_loc.id)
                wh.rental_in_location_id = in_loc.id
            if not wh.rental_out_location_id:
                out_loc = slo.with_context(lang='en_US').search([
                    ('name', 'ilike', 'Rental Out'),
                    ('location_id', '=', wh.rental_view_location_id.id),
                    ], limit=1)
                if not out_loc:
                    out_loc = slo.with_context(lang='en_US').create({
                        'name': 'Rental Out',
                        'location_id': wh.rental_view_location_id.id,
                        })
                    slo.browse(out_loc.id).name = _('Rental Out')
                    logger.debug(
                        'New out rental stock location created ID %d',
                        out_loc.id)
                wh.rental_out_location_id = out_loc.id

    def write(self, vals):
        if 'rental_allowed' in vals:
            rental_route = self.env.ref('sale_rental.route_warehouse0_rental')
            sell_rented_route = self.env.ref(
                'sale_rental.route_warehouse0_sell_rented_product')
            if vals.get('rental_allowed'):
                self._create_rental_locations()
                self.write({
                    'route_ids': [(4, rental_route.id)],
                    'rental_route_id': rental_route.id,
                    'sell_rented_product_route_id': sell_rented_route.id,
                    })
                for rule_vals in self._get_rental_push_pull_rules():
                    self.env['stock.rule'].create(rule_vals)
            else:
                for wh in self:
                    pull_rules_to_delete = self.env['stock.rule'].search(
                        [
                            ('route_id', 'in', (
                                wh.rental_route_id.id,
                                wh.sell_rented_product_route_id.id)),
                            ('location_src_id', 'in', (
                                wh.rental_out_location_id.id,
                                wh.rental_in_location_id.id)),
                            ('action', '=', 'move')])
                    pull_rules_to_delete.unlink()
                    push_rule_to_delete =\
                        self.env['stock.rule'].search([
                            ('route_id', '=', wh.rental_route_id.id),
                            ('location_from_id', '=',
                                wh.rental_out_location_id.id),
                            ('location_dest_id', '=',
                                wh.rental_in_location_id.id)])
                    push_rule_to_delete.unlink()
                    wh.write({
                        'route_ids': [(3, rental_route.id)],
                        'rental_route_id': False,
                        'sell_rented_product_route_id': False,
                    })
        return super(StockWarehouse, self).write(vals)


class StockRule(models.Model):
    _inherit = 'stock.rule'

    def _push_prepare_move_copy_values(self, move_to_copy, new_date):
        """Inherit to write the end date of the rental on the return move"""
        res = super(StockRule, self)._push_prepare_move_copy_values(
            move_to_copy, new_date)
        location_id = res.get('location_id', False)
        if location_id and\
            location_id ==\
            move_to_copy.warehouse_id.rental_out_location_id.id and\
                move_to_copy.sale_line_id and\
                move_to_copy.sale_line_id.rental_type == 'new_rental':
            rental_end_date = move_to_copy.sale_line_id.end_date
            res['date_expected'] = fields.Datetime.to_datetime(rental_end_date)
        return res


class StockInventory(models.Model):
    _inherit = 'stock.inventory'

    def create_demo_and_validate(self):
        silo = self.env['stock.inventory.line']
        demo_inv = self.env.ref('sale_rental.rental_inventory')
        rental_in_loc = self.env.ref('stock.warehouse0').rental_in_location_id
        demo_inv.location_id = rental_in_loc
        demo_inv.action_start()
        products = [
            ('product.consu_delivery_01', 56),
            ('product.product_product_20', 46),
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
        demo_inv.action_validate()
        return True
