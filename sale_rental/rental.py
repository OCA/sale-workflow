# -*- encoding: utf-8 -*-
##############################################################################
#
#    Sale Rental module for OpenERP
#    Copyright (C) 2014 Akretion (http://www.akretion.com)
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

from openerp.osv import orm, fields
from openerp.tools.translate import _
from openerp import netsvc
from datetime import datetime, timedelta
from openerp.tools import DEFAULT_SERVER_DATE_FORMAT
from openerp.tools import DEFAULT_SERVER_DATETIME_FORMAT
from dateutil.relativedelta import relativedelta
import logging

logger = logging.getLogger(__name__)
# TODO : block if we sell a rented product already sold => state


class product_product(orm.Model):
    _inherit = 'product.product'

    _columns = {
        # Link rental service -> rented HW product
        'rented_product_id': fields.many2one(
            'product.product', 'Related Rented Product',
            domain=[('type', 'in', ('product', 'consu'))]),
        # Link rented HW product -> rental service
        'rental_service_ids': fields.one2many(
            'product.product', 'rented_product_id', 'Related Rental Services'),
        }

    def _check_rental(self, cr, uid, ids):
        for product in self.browse(cr, uid, ids):
            if product.rented_product_id and product.type != 'service':
                raise orm.except_orm(
                    _("Error:"),
                    _("The rental product '%s' must be of type 'Service'.")
                    % product.name)
            if product.rented_product_id and not product.must_have_dates:
                raise orm.except_orm(
                    _("Error:"),
                    _("The rental product '%s' must have the option "
                        "''Must Have Start and End Dates' checked.")
                    % product.name)
            (model, time_uom_categ_id) = self.pool['ir.model.data'].\
                get_object_reference(cr, uid, 'product', 'uom_categ_wtime')
            assert model == 'product.uom.categ', 'Must be a product uom categ'
            if (
                    product.rented_product_id and
                    product.uom_id.category_id.id != time_uom_categ_id):
                raise orm.except_orm(
                    _("Error:"),
                    _("The rental product '%s' must have a unit of measure "
                        "that belong to the 'Time' category.")
                    % product.name)
        return True

    _constraints = [(
        _check_rental, "error msg in raise",
        ['rented_product_id', 'must_have_dates']
    )]


class sale_order(orm.Model):
    _inherit = 'sale.order'

    def _prepare_order_line_procurement(
            self, cr, uid, order, line, move_id, date_planned, context=None):
        if context is None:
            context = {}
        res = super(sale_order, self)._prepare_order_line_procurement(
            cr, uid, order, line, move_id, date_planned, context=context)
        if context.get('rent') == 'out':
            res.update({
                'product_id': line.product_id.rented_product_id.id,
                'product_qty': 1,
                'product_uos_qty': 1,
                'product_uom': line.product_id.rented_product_id.uom_id.id,
                'product_uos': line.product_id.rented_product_id.uom_id.id,
                'location_id':
                order.shop_id.warehouse_id.rental_in_location_id.id,
                #'procure_method': , #?????
                })
        return res

    def _prepare_order_line_move(
            self, cr, uid, order, line, picking_id, date_planned,
            context=None):
        if context is None:
            context = {}
        res = super(sale_order, self)._prepare_order_line_move(
            cr, uid, order, line, picking_id, date_planned, context=context)
        rent_type = context.get('rent')
        if rent_type:
            loc_rent_in = order.shop_id.warehouse_id.rental_in_location_id.id
            loc_rent_out = order.shop_id.warehouse_id.rental_out_location_id.id
            if rent_type == 'out':
                location_id = loc_rent_in
                location_dest_id = loc_rent_out
            elif rent_type == 'in':
                location_id = loc_rent_out
                location_dest_id = loc_rent_in
            res.update({
                'product_id': line.product_id.rented_product_id.id,
                'product_qty': 1,
                'product_uos_qty': 1,
                'product_uom': line.product_id.rented_product_id.uom_id.id,
                'product_uos': line.product_id.rented_product_id.uom_id.id,
                'location_id': location_id,
                'location_dest_id': location_dest_id,
                'product_packaging': (
                    line.product_id.rented_product_id.packaging
                    and line.product_id.rented_product_id.packaging[0].id
                    or False),
                'price_unit':
                line.product_id.rented_product_id.standard_price or 0.0,
                'move_dest_id': context.get('in_move_id', False),
                })
        if line.sell_rental_id:
            res.update({
                'prodlot_id': line.sell_rental_id.prodlot_id.id,
                'location_id':
                order.shop_id.warehouse_id.rental_out_location_id.id,
                })
        return res

    def _prepare_order_picking_rent_in(
            self, cr, uid, order, date, context=None):
        return {
            'name': self.pool['ir.sequence'].get(cr, uid, 'stock.picking.in'),
            'origin': order.name,
            'date': self.date_to_datetime(cr, uid, date, context),
            'type': 'in',
            'state': 'auto',
            'move_type': order.picking_policy,
            'sale_id': order.id,
            'partner_id': order.partner_shipping_id.id,
            'note': order.note,
            'invoice_state': 'none',
            'company_id': order.company_id.id,
        }

    def _prepare_rental(self, cr, uid, line, out_move_id, context=None):
        return {
            'start_order_line_id': line.id,
            'out_move_id': out_move_id,
            }

    def _create_pickings_and_procurements(
            self, cr, uid, order, order_lines, picking_id=False, context=None):
        picking_obj = self.pool['stock.picking']
        proc_obj = self.pool['procurement.order']
        move_obj = self.pool['stock.move']
        wf_service = netsvc.LocalService("workflow")
        if context is None:
            context = {}
        picking_out_id = False
        picking_in_dict = {}  # key = date ; value = ID
        proc_ids = []
        rent_out_ctx = context.copy()
        rent_out_ctx['rent'] = 'out'
        rent_in_ctx = context.copy()
        rent_in_ctx['rent'] = 'in'
        for line in order_lines:
            if line.sell_rental_id:
                # Cancel return picking
                wf_service.trg_validate(
                    uid, 'stock.picking', line.sell_rental_id.in_picking_id.id,
                    'button_cancel', cr)
            if line.product_id.rented_product_id:
                if line.rental_type == 'rental_extension':
                    if not line.extension_rental_id:
                        raise orm.except_orm(
                            _('Error:'),
                            _("Missing Rental Extension for Sale Order Line "
                                "with description '%s'")
                            % line.name)
                    new_datetime = self.date_to_datetime(
                        cr, uid, line.end_date, context)
                    move_obj.write(
                        cr, uid, line.extension_rental_id.in_move_id.id, {
                            'date': new_datetime,
                            'date_expected': new_datetime,
                        }, context=context)
                    picking_obj.write(
                        cr, uid, line.extension_rental_id.in_picking_id.id, {
                            'date': line.end_date,
                        }, context=context)
                elif line.rental_type == 'new_rental':
                    start_datetime = self.date_to_datetime(
                        cr, uid, line.start_date, context)
                    date_planned = datetime.strptime(
                        start_datetime, DEFAULT_SERVER_DATETIME_FORMAT)
                    date_planned = (
                        date_planned - timedelta(
                            days=order.company_id.security_lead)).strftime(
                        DEFAULT_SERVER_DATETIME_FORMAT)

                    if not picking_out_id:
                        picking_out_id = picking_obj.create(
                            cr, uid, self._prepare_order_picking(
                                cr, uid, order, context=rent_out_ctx),
                            context=context)
                        # No pb to keep the native code, unless for date
                        # but if we have both in the same...

                    # Create return picking
                    if line.end_date not in picking_in_dict:
                        picking_in_id = picking_obj.create(
                            cr, uid, self._prepare_order_picking_rent_in(
                                cr, uid, order, line.end_date,
                                context=context),
                            context=context)
                        picking_in_dict[line.end_date] = picking_in_id
                    else:
                        picking_in_id = picking_in_dict[line.end_date]

                    end_datetime = self.date_to_datetime(
                        cr, uid, line.end_date, context)

                    in_move_id = move_obj.create(
                        cr, uid, self._prepare_order_line_move(
                            cr, uid, order, line, picking_in_id,
                            end_datetime, context=rent_in_ctx),
                        context=context)

                    # Create outgoing picking
                    rent_out_ctx['in_move_id'] = in_move_id
                    out_move_id = move_obj.create(
                        cr, uid, self._prepare_order_line_move(
                            cr, uid, order, line, picking_out_id,
                            date_planned, context=rent_out_ctx),
                        context=context)
                    proc_id = proc_obj.create(
                        cr, uid, self._prepare_order_line_procurement(
                            cr, uid, order, line, out_move_id,
                            date_planned, context=rent_out_ctx),
                        context=context)
                    proc_ids.append(proc_id)
                    line.write({'procurement_id': proc_id})
#                    self.ship_recreate(
#                        cr, uid, order, line, out_move_id, proc_id)

                    self.pool['sale.rental'].create(
                        cr, uid, self._prepare_rental(
                            cr, uid, line, out_move_id, context=context),
                        context=context)

        for proc_id in proc_ids:
            wf_service.trg_validate(
                uid, 'procurement.order', proc_id, 'button_confirm', cr)
        for picking_in_id in picking_in_dict.values():
            wf_service.trg_validate(
                uid, 'stock.picking', picking_in_id, 'button_confirm', cr)
        res = super(sale_order, self)._create_pickings_and_procurements(
            cr, uid, order, order_lines, picking_id=picking_out_id,
            context=context)
        return res


class sale_order_line(orm.Model):
    _inherit = 'sale.order.line'

    _columns = {
        'rental': fields.boolean('Rental'),
        'can_sell_rental': fields.boolean('Can Sell from Rental'),
        'rental_type': fields.selection([
            ('new_rental', 'New Rental'),
            ('rental_extension', 'Rental Extension'),
            ], 'Rental Type',
            readonly=True, states={'draft': [('readonly', False)]}),
        'extension_rental_id': fields.many2one(
            'sale.rental', 'Rental to Extend'),
        'sell_rental_id': fields.many2one(
            'sale.rental', 'Rental to Sell'),
        # TODO : related one2many + impact sur rental
        }

    def start_end_dates_change(
            self, cr, uid, ids, start_date, end_date, product_id,
            product_uom_qty, context=None):
        res = super(sale_order_line, self).start_end_dates_change(
            cr, uid, ids, start_date, end_date, product_id,
            product_uom_qty, context=context)
        if 'value' not in res:
            res['value'] = {}
        if start_date and end_date and product_id:
            product = self.pool['product.product'].browse(
                cr, uid, product_id, context=context)
            if product.rented_product_id:
                start_date_dt = datetime.strptime(
                    start_date, DEFAULT_SERVER_DATE_FORMAT)
                end_date_dt = datetime.strptime(
                    end_date, DEFAULT_SERVER_DATE_FORMAT)
                days_qty = (end_date_dt - start_date_dt).days + 1
                res['value']['product_uom_qty'] = days_qty
        return res

    def product_id_change(
            self, cr, uid, ids, pricelist, product, qty=0,
            uom=False, qty_uos=0, uos=False, name='', partner_id=False,
            lang=False, update_tax=True, date_order=False, packaging=False,
            fiscal_position=False, flag=False, context=None):
        res = super(sale_order_line, self).product_id_change(
            cr, uid, ids, pricelist, product, qty=qty, uom=uom,
            qty_uos=qty_uos, uos=uos, name=name, partner_id=partner_id,
            lang=lang, update_tax=update_tax, date_order=date_order,
            packaging=packaging, fiscal_position=fiscal_position,
            flag=flag, context=context)
        if not product:
            res['value'].update({
                'rental_type': False,
                'rental': False,
                'can_sell_rental': False,
                'sell_rental_id': False,
                })
        else:
            product_o = self.pool['product.product'].browse(
                cr, uid, product, context=context)
            if product_o.rented_product_id:
                res['value'].update({
                    'rental': True,
                    })
            else:
                res['value'].update({
                    'rental_type': False,
                    'rental': False,
                    })
            if product_o.rental_service_ids:
                res['value']['can_sell_rental'] = True
            else:
                res['value'].update({
                    'can_sell_rental': False,
                    'sell_rental_id': False,
                    })
        return res

    def rental_type_change(
            self, cr, uid, ids, rental_type, product_id, context=None):
        return {}

    def extension_rental_id_change(
            self, cr, uid, ids, rental_type, extension_rental_id,
            product_id, start_date, end_date, context=None):
        res = {'value': {}}
        if (
                product_id
                and rental_type == 'rental_extension'
                and extension_rental_id):
            rental_ext = self.pool['sale.rental'].browse(
                cr, uid, extension_rental_id, context=context)
            if rental_ext.rental_product_id.id != product_id:
                raise orm.except_orm(
                    _('Error'),
                    _("The Rental Service of the Rental Extension you just "
                        "selected is '%s' and it's not the same as the "
                        "Product currently selected in this Sale Order Line.")
                    % rental_ext.rental_product_id.name)
            initial_end_date_str = rental_ext.end_date
            initial_end_date = datetime.strptime(
                initial_end_date_str, DEFAULT_SERVER_DATE_FORMAT)
            start_date = initial_end_date + relativedelta(days=1)
            res['value']['start_date'] = start_date.strftime(
                DEFAULT_SERVER_DATE_FORMAT)
        return res


class sale_rental(orm.Model):
    _name = 'sale.rental'
    _description = "Rental"
    _order = "id desc"

    def name_get(self, cr, uid, ids, context=None):
        res = []
        for rental in self.browse(cr, uid, ids, context=context):
            res.append((
                rental.id,
                u'[%s] %s (%s - %s)'
                % (
                    rental.partner_id.name,
                    rental.rented_product_id.name,
                    rental.start_date,
                    rental.end_date)))
        return res

    def _compute_end_date(self, cr, uid, ids, name, arg, context=None):
        res = {}
        for rental in self.browse(cr, uid, ids, context=context):
            end_date = False
            if rental.extension_order_line_ids:
                for extension in rental.extension_order_line_ids:
                    if extension.state not in ('cancel', 'draft'):
                        if extension.end_date > end_date:
                            end_date = extension.end_date
            if not end_date and rental.start_order_line_id:
                end_date = rental.start_order_line_id.end_date
            res[rental.id] = end_date
        return res

    _columns = {
        'start_order_line_id': fields.many2one(
            'sale.order.line', 'Rental Sale Order Line'),
        'start_date': fields.related(
            'start_order_line_id', 'start_date',
            type='date', string='Start Date', readonly=True),
        'rental_product_id': fields.related(
            'start_order_line_id', 'product_id',
            type='many2one', relation='product.product',
            string="Rental Service", readonly=True),
        'rented_product_id': fields.related(
            'rental_product_id', 'rented_product_id',
            type='many2one', relation='product.product',
            string="Rented Product", readonly=True),
        'start_order_id': fields.related(
            'start_order_line_id', 'order_id',
            type='many2one', relation='sale.order',
            string='Rental Sale Order', readonly=True),
        'company_id': fields.related(
            'start_order_id', 'company_id',
            type='many2one', relation='res.company', string='Company',
            readonly=True),
        'partner_id': fields.related(
            'start_order_id', 'partner_id',
            type='many2one', relation='res.partner', string='Partner',
            readonly=True),
        'out_move_id': fields.many2one('stock.move', 'Outgoing Stock Move'),
        'in_move_id': fields.related(
            'out_move_id', 'move_dest_id', type='many2one',
            relation='stock.move', string='Return Stock Move', readonly=True),
        'out_state': fields.related(
            'out_move_id', 'state',
            type='selection', string='State of the Outgoing Stock Move',
            selection=[
                ('draft', 'New'),
                ('cancel', 'Cancelled'),
                ('waiting', 'Waiting Another Move'),
                ('confirmed', 'Waiting Availability'),
                ('assigned', 'Available'),
                ('done', 'Done'),
                ], readonly=True),
        'in_state': fields.related(
            'in_move_id', 'state',
            type='selection', string='State of the Return Stock Move',
            selection=[
                ('draft', 'New'),
                ('cancel', 'Cancelled'),
                ('waiting', 'Waiting Another Move'),
                ('confirmed', 'Waiting Availability'),
                ('assigned', 'Available'),
                ('done', 'Done'),
                ], readonly=True),
        'out_picking_id': fields.related(
            'out_move_id', 'picking_id',
            type='many2one', relation='stock.picking', string='Delivery Order',
            readonly=True),
        'in_picking_id': fields.related(
            'in_move_id', 'picking_id',
            type='many2one', relation='stock.picking', string='Return Picking',
            readonly=True),
        'prodlot_id': fields.related(
            'out_move_id', 'prodlot_id',
            type='many2one', relation='stock.production.lot',
            string='Serial Number', readonly=True),
        'extension_order_line_ids': fields.one2many(
            'sale.order.line', 'extension_rental_id',
            'Rental Extensions', readonly=True),
        'sell_order_line_ids': fields.one2many(
            'sale.order.line', 'sell_rental_id',
            'Sell Rented Product', readonly=True),
        'end_date': fields.function(
            _compute_end_date, type='date',
            string='End Date (extensions included)',
            help="End Date of the Rental, taking into account all the "
            "extensions sold to the customer."),
        # 'state':  # TODO
        }


class stock_warehouse(orm.Model):
    _inherit = "stock.warehouse"
    _columns = {
        'rental_in_location_id': fields.many2one(
            'stock.location', 'Rental Input',
            domain=[('usage', '<>', 'view')]),
        'rental_out_location_id': fields.many2one(
            'stock.location', 'Rental Output',
            domain=[('usage', '<>', 'view')]),
    }


class stock_move(orm.Model):
    _inherit = 'stock.move'

    _columns = {
        'sale_rental_ids': fields.one2many(
            'sale.rental', 'out_move_id', 'Rentals', readonly=True),
        }

    def action_done(self, cr, uid, ids, context=None):
        '''Copy prodlot from outgoing move to incoming move'''
        res = super(stock_move, self).action_done(
            cr, uid, ids, context=context)
        for move in self.browse(cr, uid, ids, context=context):
            if (
                    move.state == 'done'
                    and move.move_dest_id
                    and move.sale_rental_ids
                    and move.prodlot_id
                    and not move.move_dest_id.prodlot_id):
                self.write(
                    cr, uid, move.move_dest_id.id, {
                        'prodlot_id': move.prodlot_id.id,
                    }, context=context)
        return res


class stock_picking(orm.Model):
    _inherit = 'stock.picking'

    # When we invoice from delivery, we shouldn't invoice the rented product
    # Beware of this: https://bugs.launchpad.net/openobject-addons/+bug/1167330
    # It will work if your code of the addons/7.0 is after 2013-12-26
    def _invoice_line_hook(self, cr, uid, move_line, invoice_line_id):
        if move_line.sale_line_id.rental:
            self.pool['account.invoice.line'].unlink(cr, uid, invoice_line_id)
        return
