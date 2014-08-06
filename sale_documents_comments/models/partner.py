# -*- encoding: utf-8 -*-
##############################################################################
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
#    along with this program.  If not, see http://www.gnu.org/licenses/.
#
##############################################################################

from openerp.osv import orm, fields


class ResPartner(orm.Model):
    _inherit = 'res.partner'

    _columns = {
        'sale_comment': fields.text('Comments for sale orders'),
        'sale_propagated_comment': fields.text('Propagated comments for sale'
                                               ' orders'),
        'picking_comment': fields.text('Comments for pickings'),
        'picking_propagated_comment': fields.text('Propagated comments for'
                                                  ' pickings'),
        'invoice_comment': fields.text('Comments for invoices'),
    }
