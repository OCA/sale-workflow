# -*- encoding: utf-8 -*-
##############################################################################
#
#    Sale - Sale Order Mass Action module for Odoo
#    Copyright (C) 2015-Today GRAP (http://www.grap.coop)
#    @author Sylvain LE GAL (https://twitter.com/legalsylvain)
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

from openerp.osv import fields
from openerp.osv.orm import TransientModel


class SaleOrderMassActionWizard(TransientModel):
    _name = 'sale.order.mass.action.wizard'

    _columns = {
        'confirm': fields.boolean(
            'Confirm', help="""check this box if you want to"""
            """ confirm all the selected quotations."""),
    }

    _defaults = {
        'confirm': True,
    }

    def apply_button(self, cr, uid, ids, context=None):
        context = context or {}
        so_obj = self.pool['sale.order']
        wizard = self.browse(cr, uid, ids[0], context=context)
        if wizard.confirm:
            so_ids = so_obj.search(cr, uid, [
                ('id', 'in', context.get('active_ids')),
                ('state', '=', 'draft')], context=context)
            for so_id in so_ids:
                so_obj.action_button_confirm(cr, uid, [so_id], context=context)
        return True
