# -*- coding: utf-8 -*-
###############################################################################
#    
#    OpenERP, Open Source Management Solution
#    Copyright (C) 2012 Savoir-faire Linux (<http://www.savoirfairelinux.com>).
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
###############################################################################

from osv import fields, osv

class sale_order(osv.osv):
    _name = 'sale.order'
    _inherit = 'sale.order'

    def edi_export(self, cr, uid, records, edi_struct=None, context=None):
       return super(sale_order, self).edi_export(cr, uid, records, edi_struct,
              context)


sale_order()
