# -*- coding: utf-8 -*-
#
#
#    Copyright (C) 2012 Agile Business Group sagl (<http://www.agilebg.com>)
#    Copyright (C) 2012 Domsense srl (<http://www.domsense.com>)
#
#    This program is free software: you can redistribute it and/or modify
#    it under the terms of the GNU Affero General Public License as published
#    by the Free Software Foundation, either version 3 of the License, or
#    (at your option) any later version.
#
#    This program is distributed in the hope that it will be useful,
#    but WITHOUT ANY WARRANTY; without even the implied warranty of
#    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#    GNU General Public License for more details.
#
#    You should have received a copy of the GNU Affero General Public License
#    along with this program.  If not, see <http://www.gnu.org/licenses/>.
#
#

from openerp.osv import fields, orm
from openerp.tools.translate import _
import openerp.addons.decimal_precision as dp


class sale_delivery_term(orm.Model):
    _name = 'sale.delivery.term'
    _columns = {
        'name': fields.char('Name', size=64, required=True),
        'line_ids': fields.one2many(
            'sale.delivery.term.line', 'term_id', 'Lines', required=True),
        'company_id': fields.many2one(
            'res.company', 'Company', required=True, select=1),
    }
    _defaults = {
        'company_id': lambda self, cr, uid, c: self.pool.get(
            'res.company')._company_default_get(
                cr, uid, 'sale.delivery.term', context=c),
    }

    def is_total_percentage_correct(self, cr, uid, term_ids, context=None):
        for term in self.browse(cr, uid, term_ids, context=context):
            total = 0.0
            for line in term.line_ids:
                total += line.quantity_perc
            if total != 1:
                return False
        return True


class sale_delivery_term_line(orm.Model):

    _name = 'sale.delivery.term.line'
    _rec_name = 'term_id'
    _columns = {
        'term_id': fields.many2one(
            'sale.delivery.term', 'Term', ondelete='cascade'),
        'quantity_perc': fields.float(
            'Quantity percentage', required=True,
            help="For 20% set '0.2'",
            digits_compute=dp.get_precision('Sale Delivery Term')),
        'delay': fields.float(
            'Delivery Lead Time', required=True,
            help="Number of days between the order confirmation and the "
                 "shipping of the products to the customer"),
    }


class sale_order_line_master(orm.Model):

    def _clean_on_change_dict(self, res_dict):
        if 'delay' in res_dict['value']:
            del res_dict['value']['delay']
        if 'th_weight' in res_dict['value']:
            del res_dict['value']['th_weight']
        if 'type' in res_dict['value']:
            del res_dict['value']['type']
        if 'tax_id' in res_dict['value']:
            res_dict['value']['tax_ids'] = res_dict['value']['tax_id']
            del res_dict['value']['tax_id']
        return res_dict

    def product_id_change(
        self, cr, uid, ids, pricelist, product, qty=0,
        uom=False, qty_uos=0, uos=False, name='', partner_id=False,
        lang=False, update_tax=True, date_order=False, packaging=False,
        fiscal_position=False, flag=False, context=None
    ):
        res = self.pool.get(
            'sale.order.line').product_id_change(
                cr, uid, ids, pricelist, product, qty=qty,
                uom=uom, qty_uos=qty_uos, uos=uos, name=name,
                partner_id=partner_id,
                lang=lang, update_tax=update_tax, date_order=date_order,
                packaging=packaging, fiscal_position=fiscal_position,
                flag=flag, context=context)
        return self._clean_on_change_dict(res)

    def product_uom_change(
        self, cursor, user, ids, pricelist, product, qty=0,
        uom=False, qty_uos=0, uos=False, name='', partner_id=False,
        lang=False, update_tax=True, date_order=False, context=None
    ):
        res = self.pool.get(
            'sale.order.line').product_uom_change(
                cursor, user, ids, pricelist, product, qty=qty,
                uom=uom, qty_uos=qty_uos, uos=uos, name=name,
                partner_id=partner_id,
                lang=lang, update_tax=update_tax, date_order=date_order,
                context=context)
        return self._clean_on_change_dict(res)

    def product_packaging_change(
        self, cr, uid, ids, pricelist, product, qty=0, uom=False,
        partner_id=False, packaging=False, flag=False, context=None
    ):
        return self.pool.get('sale.order.line').product_packaging_change(
            cr, uid, ids, pricelist, product, qty=qty, uom=uom,
            partner_id=partner_id, packaging=packaging, flag=flag,
            context=context)

    def _amount_line(self, cr, uid, ids, field_name, arg, context=None):
        tax_obj = self.pool.get('account.tax')
        cur_obj = self.pool.get('res.currency')
        res = {}
        if context is None:
            context = {}
        for line in self.browse(cr, uid, ids, context=context):
            price = line.price_unit * (1 - (line.discount or 0.0) / 100.0)
            taxes = tax_obj.compute_all(
                cr, uid, line.tax_ids, price,
                line.product_uom_qty, line.order_id.partner_invoice_id.id,
                line.product_id, line.order_id.partner_id)
            cur = line.order_id.pricelist_id.currency_id
            res[line.id] = cur_obj.round(cr, uid, cur, taxes['total'])
        return res

    def _get_uom_id(self, cr, uid, *args):
        return self.pool.get('sale.order.line')._get_uom_id(cr, uid, args)

    _name = 'sale.order.line.master'
    _columns = {
        'order_id': fields.many2one(
            'sale.order', 'Order Reference', required=True,
            ondelete='cascade'),
        'delivery_term_id': fields.many2one(
            'sale.delivery.term', 'Delivery term',
            required=True, ondelete='restrict'),
        'name': fields.char('Description', size=256, required=True),
        'product_id': fields.many2one(
            'product.product', 'Product',
            domain=[('sale_ok', '=', True)]),
        'price_unit': fields.float(
            'Unit Price', required=True,
            digits_compute=dp.get_precision('Product Price')),
        'price_subtotal': fields.function(_amount_line, string='Subtotal',
                                          digits_compute=dp.get_precision(
                                              'Product Price')),
        'product_uom_qty': fields.float(
            'Quantity (UoM)', digits_compute=dp.get_precision('Product UoS'),
            required=True),
        'product_uom': fields.many2one(
            'product.uom', 'Unit of Measure ', required=True),
        'product_uos_qty': fields.float(
            'Quantity (UoS)', digits_compute=dp.get_precision('Product UoS')),
        'product_uos': fields.many2one('product.uom', 'Product UoS'),
        'product_packaging': fields.many2one('product.packaging', 'Packaging'),
        'order_line_ids': fields.one2many(
            'sale.order.line', 'master_line_id', 'Detailed lines'),
        'discount': fields.float('Discount (%)', digits=(16, 2)),
        'tax_ids': fields.many2many(
            'account.tax', 'sale_master_order_line_tax', 'order_line_id',
            'tax_id', 'Taxes'),
    }
    _defaults = {
        'product_uom': _get_uom_id,
        'product_uom_qty': 1,
        'product_uos_qty': 1,
        'product_packaging': False,
        'price_unit': 0.0,
    }

    def _prepare_order_line(
        self, cr, uid, term_line, master_line, group_index=0, context=None
    ):
        order_line_pool = self.pool.get('sale.order.line')
        group_pool = self.pool.get('sale.order.line.group')
        group_ids = group_pool.search(cr, uid, [])
        product_uom_qty = master_line.product_uom_qty * term_line.quantity_perc
        product_uos_qty = master_line.product_uos_qty * term_line.quantity_perc
        order_line_vals = {}
        on_change_res = order_line_pool.product_id_change(
            cr, uid, [], master_line.order_id.pricelist_id.id,
            master_line.product_id.id, qty=product_uom_qty,
            uom=master_line.product_uom.id, qty_uos=product_uos_qty,
            uos=master_line.product_uos.id, name=master_line.name,
            partner_id=master_line.order_id.partner_id.id,
            lang=False, update_tax=True,
            date_order=master_line.order_id.date_order,
            packaging=master_line.product_packaging.id,
            fiscal_position=master_line.order_id.fiscal_position.id,
            flag=False, context=context)
        order_line_vals.update(on_change_res['value'])
        order_line_vals.update({
            'order_id': master_line.order_id.id,
            'name': master_line.name,
            'price_unit': master_line.price_unit,
            'product_uom_qty': product_uom_qty,
            'product_uom': master_line.product_uom.id,
            'product_id': (
                master_line.product_id and master_line.product_id.id or False),
            'product_uos_qty': product_uos_qty,
            'product_uos': (
                master_line.product_uos.id
                if master_line.product_uos
                else False),
            'product_packaging': master_line.product_packaging.id,
            'master_line_id': master_line.id,
            'delay': term_line.delay,
            'picking_group_id': group_ids[group_index],
            'tax_id': [(6, 0, [tax.id for tax in master_line.tax_ids])],
        })
        return order_line_vals

    def generate_detailed_lines(self, cr, uid, ids, context=None):
        group_pool = self.pool.get('sale.order.line.group')
        order_line_pool = self.pool.get('sale.order.line')
        group_ids = group_pool.search(cr, uid, [])
        for master_line in self.browse(cr, uid, ids):
            if master_line.order_line_ids:
                raise orm.except_orm(
                    _('Error'),
                    _("Detailed lines generated yet (for master line '%s'). "
                      "Remove them first") % master_line.name)
            if len(master_line.delivery_term_id.line_ids) > len(group_ids):
                raise orm.except_orm(
                    _('Error'),
                    _("Delivery term lines are %d. Order line groups are %d. "
                      "Please create more groups")
                    % (len(master_line.delivery_term_id.line_ids),
                        len(group_ids)))
            if not master_line.delivery_term_id.is_total_percentage_correct():
                raise orm.except_orm(
                    _('Error'),
                    _("Total percentage of delivery term %s is not equal to 1")
                    % master_line.delivery_term_id.name)
            for group_index, term_line in enumerate(
                master_line.delivery_term_id.line_ids
            ):
                order_line_vals = self._prepare_order_line(
                    cr, uid, term_line, master_line, group_index=group_index,
                    context=context)
                order_line_pool.create(
                    cr, uid, order_line_vals, context=context)
        return True

    def copy_data(self, cr, uid, id, default=None, context=None):
        if not default:
            default = {}
        default.update({
            'order_line_ids': [],
        })
        return super(sale_order_line_master, self).copy_data(
            cr, uid, id, default, context=context)

    def check_master_line_total(self, cr, uid, ids, context=None):
        for master_line in self.browse(cr, uid, ids, context):
            master_uom_qty = master_line.product_uom_qty
            master_uos_qty = master_line.product_uos_qty
            total_uom_qty = 0.0
            total_uos_qty = 0.0
            for order_line in master_line.order_line_ids:
                total_uom_qty += order_line.product_uom_qty
                total_uos_qty += order_line.product_uos_qty
            if master_uom_qty != total_uom_qty:
                raise orm.except_orm(
                    _('Error'),
                    _('Order lines total quantity %s is different from master '
                      'line quantity %s') % (total_uom_qty, master_uom_qty))
            if master_uos_qty != total_uos_qty:
                raise orm.except_orm(
                    _('Error'),
                    _('Order lines total quantity %s is different from master '
                      'line quantity %s') % (total_uos_qty, master_uos_qty))


class sale_order_line(orm.Model):
    _inherit = 'sale.order.line'
    _columns = {
        'master_line_id': fields.many2one(
            'sale.order.line.master', 'Master Line'),
    }

    def copy_data(self, cr, uid, id, default=None, context=None):
        if not default:
            default = {}
        default.update({'master_line_id': False})
        return super(sale_order_line, self).copy_data(
            cr, uid, id, default, context=context)


class sale_order(orm.Model):
    _inherit = 'sale.order'
    _columns = {
        'master_order_line': fields.one2many(
            'sale.order.line.master', 'order_id', 'Master Order Lines',
            readonly=True, states={'draft': [('readonly', False)]}),
    }

    def copy(self, cr, uid, id, default=None, context=None):
        if not default:
            default = {}
        default.update({
            'order_line': [],
        })
        return super(sale_order, self).copy(
            cr, uid, id, default, context=context)

    def generate_detailed_lines(self, cr, uid, ids, context=None):
        for order in self.browse(cr, uid, ids, context):
            for master_line in order.master_order_line:
                master_line.generate_detailed_lines()
        return True

    def action_wait(self, cr, uid, ids, context=None):
        for order in self.browse(cr, uid, ids, context):
            for master_line in order.master_order_line:
                master_line.check_master_line_total()
        return super(sale_order, self).action_wait(
            cr, uid, ids, context=context)
