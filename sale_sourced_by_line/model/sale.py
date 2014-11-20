# -*- coding: utf-8 -*-
#
#
#    Author: Guewen Baconnier, Yannick Vaucher
#    Copyright 2013-2014 Camptocamp SA
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
#

from openerp.osv import orm, fields


class sale_order(orm.Model):
    _inherit = 'sale.order'

    def _prepare_order_line_procurement(self, cr, uid, order, line,
                                        group_id=False, context=None):
        values = super(sale_order, self)._prepare_order_line_procurement(
            cr, uid, order, line, group_id=group_id, context=context)
        if line.warehouse_id:
            values['warehouse_id'] = line.warehouse_id.id
        return values

    ###
    # OVERRIDE to consider sale_order's warehouse_id as default
    ###
    def action_ship_create(self, cr, uid, ids, context=None):
        """Create the required procurements to supply sales order lines, also
        connecting the procurements to appropriate stock moves in order to
        bring the goods to the sales order's requested location.

        :return: True
        """
        procurement_obj = self.pool.get('procurement.order')
        sale_line_obj = self.pool.get('sale.order.line')
        for order in self.browse(cr, uid, ids, context=context):
            proc_ids = []

            groups = {}

            for line in order.order_line:
                group_id = groups.get(line.warehouse_id)
                if not group_id:
                    vals = self._prepare_procurement_group(cr, uid, order,
                                                           context=context)
                    group_id = self.pool["procurement.group"].create(
                        cr, uid, vals, context=context)
                    groups[line.warehouse_id] = group_id
                line.write({'procurement_group_id': group_id})
                # Try to fix exception procurement (possible when after a
                # shipping exception the user choose to recreate)
                if line.procurement_ids:
                    # first check them to see if they are in exception or not
                    # (one of the related moves is cancelled)
                    procurement_obj.check(
                        cr, uid, [x.id for x in line.procurement_ids
                                  if x.state not in ['cancel', 'done']])
                    line.refresh()
                    # run again procurement that are in exception in order to
                    # trigger another move
                    proc_ids += [x.id for x in line.procurement_ids
                                 if x.state in ('exception', 'cancel')]
                elif sale_line_obj.need_procurement(cr, uid, [line.id],
                                                    context=context):
                    if (line.state == 'done') or not line.product_id:
                        continue
                    vals = self._prepare_order_line_procurement(
                        cr, uid, order, line,
                        group_id=group_id, context=context)
                    proc_id = procurement_obj.create(
                        cr, uid, vals, context=context)
                    proc_ids.append(proc_id)
            # Confirm procurement order such that rules will be applied on it
            # note that the workflow normally ensure proc_ids isn't an empty
            # list
            procurement_obj.run(cr, uid, proc_ids, context=context)

            # if shipping was in exception and the user choose to recreate the
            # delivery order, write the new status of SO
            if order.state == 'shipping_except':
                val = {'state': 'progress', 'shipped': False}

                if (order.order_policy == 'manual'):
                    for line in order.order_line:
                        if ((not line.invoiced)
                                and (line.state not in ('cancel', 'draft'))):
                            val['state'] = 'manual'
                            break
                order.write(val)
        return True

    ###
    # OVERRIDE to use sale.order.line's procurement_group_id from lines
    ###
    def _get_shipped(self, cr, uid, ids, name, args, context=None):
        """ As procurement is per sale line basis, we check each line

            If at least a line has no procurement group defined, it means it
            isn't shipped yet.

            Only when all procurement are done or cancelled, we consider
            the sale order as being shipped.

            And if there is no line, we have nothing to ship, thus it isn't
            shipped.

        """
        res = {}
        for sale in self.browse(cr, uid, ids, context=context):
            if not sale.order_line:
                res[sale.id] = False
                continue

            groups = set([line.procurement_group_id
                          for line in sale.order_line])
            is_shipped = True
            for group in groups:
                if not group:
                    is_shipped = False
                    break
                is_shipped &= all([proc.state in ['cancel', 'done']
                                   for proc in group.procurement_ids])
            res[sale.id] = is_shipped
        return res

    def _get_orders_procurements(self, cr, uid, ids, context=None):
        res = set()
        proc_orders = self.pool['procurement.order'].browse(
            cr, uid, ids, context=context)
        for proc in proc_orders:
            if proc.state == 'done' and proc.sale_line_id:
                res.add(proc.sale_line_id.order_id.id)
        return list(res)

    ###
    # OVERRIDE to find sale.order.line's picking
    ###
    def _get_picking_ids(self, cr, uid, ids, name, args, context=None):
        res = {}
        for sale in self.browse(cr, uid, ids, context=context):
            group_ids = set([line.procurement_group_id.id
                             for line in sale.order_line
                             if line.procurement_group_id])
            if not any(group_ids):
                res[sale.id] = []
                continue
            res[sale.id] = self.pool['stock.picking'].search(
                cr, uid, [('group_id', 'in', list(group_ids))],
                context=context)
        return res

    _columns = {
        'warehouse_id': fields.many2one(
            'stock.warehouse',
            'Default Warehouse',
            help="If no source warehouse is selected on line, "
                 "this warehouse is used as default. "),
        'shipped': fields.function(
            _get_shipped, string='Delivered', type='boolean',
            store={
                'procurement.order': (_get_orders_procurements, ['state'], 10)
            }),
        'picking_ids': fields.function(
            _get_picking_ids, method=True, type='one2many',
            relation='stock.picking',
            string='Picking associated to this sale'),
    }


class sale_order_line(orm.Model):
    _inherit = 'sale.order.line'

    _columns = {
        'warehouse_id': fields.many2one(
            'stock.warehouse',
            'Source Warehouse',
            help="If a source warehouse is selected, "
                 "it will be used to define the route. "
                 "Otherwise, it will get the warehouse of "
                 "the sale order"),
        'procurement_group_id': fields.many2one(
            'procurement.group',
            'Procurement group',
            copy=False),
    }
