# -*- encoding: utf-8 -*-
##############################################################################
#
#    OpenERP, Open Source Management Solution
#    This module copyright (C) 2014 Savoir-faire Linux
#    (<http://www.savoirfairelinux.com>).
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

import json
from lxml import etree

from openerp.tools.safe_eval import safe_eval
from openerp.osv import orm, fields


class SaleOrder(orm.Model):
    _inherit = 'sale.order'

    def _get_addresses(self, cr, uid, ids, field_names, arg, context=None):
        """ Get formatted addresses for partner fields """
        partner_obj = self.pool['res.partner']
        res = {}
        for so in self.browse(cr, uid, ids, context=context):
            res[so.id] = val = {
                'ui_partner_address': '',
                'ui_invoice_address': '',
                'ui_deliver_address': '',
            }

            if so.partner_id:
                val['ui_partner_address'] = partner_obj._display_address(
                    cr, uid, so.partner_id, context=context)
            if so.partner_invoice_id:
                val['ui_invoice_address'] = partner_obj._display_address(
                    cr, uid, so.partner_invoice_id, context=context)
            if so.partner_shipping_id:
                val['ui_deliver_address'] = partner_obj._display_address(
                    cr, uid, so.partner_shipping_id, context=context)

        return res

    _columns = {
        'ui_partner_address': fields.function(_get_addresses, method=True,
                                              type='text', store=False,
                                              multi='partner addresses'),
        'ui_invoice_address': fields.function(_get_addresses, method=True,
                                              type='text', store=False,
                                              multi='partner addresses'),
        'ui_deliver_address': fields.function(_get_addresses, method=True,
                                              type='text', store=False,
                                              multi='partner addresses'),
    }

    def fields_view_get(self, cr, uid, view_id=None, view_type='form',
                        context=None, toolbar=False, submenu=False):
        """ Overriden to:
            - Remove 'show_address' from partner field contexts
            - Add on_change on on partner_field contexts where applicable
        """
        res = super(SaleOrder, self).fields_view_get(
            cr, uid, view_id=view_id, view_type=view_type, context=context,
            toolbar=toolbar, submenu=submenu)

        if view_type == 'form':
            arch = etree.fromstring(res['arch'])
            for (ui, base, add_onchange) in [
                    ('ui_partner_address', 'partner_id', False),
                    ('ui_invoice_address', 'partner_invoice_id', True),
                    ('ui_deliver_address', 'partner_shipping_id', True),
            ]:
                field = arch.xpath("//field[@name='{0}']".format(base))
                if field and field[0].attrib['context']:
                    field = field[0]
                    context = safe_eval(field.attrib['context'])
                    context.pop('show_address', None)
                    field.attrib['context'] = json.dumps(context)
                    if add_onchange:
                        field.attrib['on_change'] = (
                            "onchange_partner_address('{0}', {1}, context)"
                            .format(ui, base))

            res['arch'] = etree.tostring(arch)

        return res

    def onchange_partner_address(self, cr, uid, ids, ui_field, partner_id,
                                 context=None):
        """
        on_change partner, write the address in the corresponding ui field
        """
        res = {}
        if partner_id:
            partner_obj = self.pool['res.partner']
            partner = partner_obj.browse(cr, uid, partner_id)
            addr = partner_obj._display_address(cr, uid, partner,
                                                context=context)
            res['value'] = {ui_field: addr}
        else:
            res['value'] = {ui_field: ''}

        return res

    def onchange_partner_id(self, cr, uid, ids, part, context=None):
        """
        override onchange_partner_id, call super() and update ui field
        """
        res = super(SaleOrder, self).onchange_partner_id(cr, uid, ids, part,
                                                         context=context)

        res.setdefault('value', {}).update(
            self.onchange_partner_address(cr, uid, ids, 'ui_partner_address',
                                          part, context=context)['value']
        )

        return res
