# -*- encoding: utf-8 -*-
##############################################################################
#                                                                            #
#  OpenERP, Open Source Management Solution.                                 #
#                                                                            #
#  @author Carlos Sánchez Cifuentes <csanchez@grupovermon.com>               #
#                                                                            #
#  This program is free software: you can redistribute it and/or modify      #
#  it under the terms of the GNU Affero General Public License as            #
#  published by the Free Software Foundation, either version 3 of the        #
#  License, or (at your option) any later version.                           #
#                                                                            #
#  This program is distributed in the hope that it will be useful,           #
#  but WITHOUT ANY WARRANTY; without even the implied warranty of            #
#  MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE. See the              #
#  GNU Affero General Public License for more details.                       #
#                                                                            #
#  You should have received a copy of the GNU Affero General Public License  #
#  along with this program. If not, see <http://www.gnu.org/licenses/>.      #
#                                                                            #
##############################################################################

from openerp.osv import fields, orm


class SaleOrderTypology(orm.Model):

    _name = 'sale.order.type'

    _description = 'Type of sale order'

    _columns = {
        'refund_journal_id': fields.many2one('account.journal',
                                             'Refund Billing Journal'),
        'description': fields.text('Description'),
        'journal_id': fields.many2one('account.journal',
                                      'Billing Journal'),
        'name': fields.char('Name', required=True),
        'sequence_id': fields.many2one('ir.sequence', 'Entry Sequence',
                                       copy=False),
        'warehouse_id': fields.many2one('stock.warehouse',
                                        'Warehouse', required=True),
    }
