# -*- encoding: utf-8 -*-
#################################################################################
#                                                                               #
#    sale_quick_payment for OpenERP                                             #
#    Copyright (C) 2011 Akretion Sébastien BEAU <sebastien.beau@akretion.com>   #
#                                                                               #
#    This program is free software: you can redistribute it and/or modify       #
#    it under the terms of the GNU Affero General Public License as             #
#    published by the Free Software Foundation, either version 3 of the         #
#    License, or (at your option) any later version.                            #
#                                                                               #
#    This program is distributed in the hope that it will be useful,            #
#    but WITHOUT ANY WARRANTY; without even the implied warranty of             #
#    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the              #
#    GNU Affero General Public License for more details.                        #
#                                                                               #
#    You should have received a copy of the GNU Affero General Public License   #
#    along with this program.  If not, see <http://www.gnu.org/licenses/>.      #
#                                                                               #
#################################################################################

from openerp.osv.orm import Model
from openerp.osv import fields
from tools.translate import _

class res_company(Model):
    """Override company to add payment configuration"""
    _inherit = "res.company"
    _columns = {        
        'sale_order_must_be_paid':fields.boolean('Sale Order Must Be Paid', 
                        help='If this option is check an order can not be validaded without payment'
                    ),
    }
