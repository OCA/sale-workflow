##############################################################################
#
#    OpenERP, Open Source Management Solution
#    Copyright (C) 2004-2009 Tiny SPRL (<http://tiny.be>).
#    Copyright (C) 2013 Agile Business Group sagl (<http://www.agilebg.com>)
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

from openerp.osv import fields, orm

class sale_order(orm.Model):
    _inherit = "sale.order"

    def copy(self, cr, uid, id, default=None, context=None):
        if default is None:
            default = {}
        default['name'] = '/'
        return super(sale_order, self).copy(cr, uid, id, default, context)

    def create(self, cr, uid, vals, context=None):
        if vals.get('name','/')=='/':
            vals['name'] = self.pool.get('ir.sequence').next_by_code(
                cr, uid, 'sale.quotation') or '/'
        return super(sale_order, self).create(cr, uid, vals, context=context)
    
    def action_wait(self, cr, uid, ids, context=None):
        if super(sale_order, self).action_wait(cr, uid, ids, context=context):
            for sale in self.browse(cr, uid, ids, context=None):
                quo = sale.name
                self.write(cr, uid, [sale.id], {
                    'origin': quo, 
                    'name': self.pool.get('ir.sequence').next_by_code(
                        cr, uid, 'sale.order')
                    })
        return True
