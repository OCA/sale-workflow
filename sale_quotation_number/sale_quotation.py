##############################################################################
#
#    OpenERP, Open Source Management Solution
#    Copyright (C) 2004-2009 Tiny SPRL (<http://tiny.be>).
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
import netsvc
import decimal_precision as dp
from osv import fields, osv

class sale_order(osv.osv):
    _inherit = "sale.order"

    def copy(self, cr, uid, id, default=None, context=None):
        if default is None:
            default = {}
        default['name'] = self.pool.get('ir.sequence').get(cr, uid, 'sale.quotation'),
        return super(sale_order, self).copy(cr, uid, id, default, context)
    
    _defaults = {
        'name': lambda obj, cr, uid, context: obj.pool.get('ir.sequence').get(cr, uid, 'sale.quotation'),
    }
    
    def action_wait(self, cr, uid, ids, *args):
        if super(sale_order, self).action_wait(cr, uid, ids, *args):
            for sale in self.browse(cr, uid, ids, context=None):
                quo = sale.name
                self.write(cr, uid, [sale.id], {'origin': quo, 'name': self.pool.get('ir.sequence').get(cr, uid, 'sale.order')})
        return True

sale_order()