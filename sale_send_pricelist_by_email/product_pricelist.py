# -*- encoding: utf-8 -*-
###############################################################################
#
#    OpenERP, Open Source Management Solution
#    This module copyright (C) 2010 - 2014 Savoir-faire Linux
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
###############################################################################

import time

from openerp.osv import fields, orm
from openerp.tools.translate import _


class ProductPricelist(orm.Model):
    _inherit = "product.pricelist"

    def _get_active_version(self, cr, uid, ids, name, args, context=None):
        res = {}
        date = context.get('date') or time.strftime('%Y-%m-%d')
        for pricelist in self.browse(cr, uid, ids, context=context):
            if pricelist.version_id:
                versions = [
                    version for version in pricelist.version_id
                    if all((
                        (version.date_start is False or
                           version.date_start <= date),
                        (version.date_end is False or
                            version.date_end >= date),
                        version.active is True
                    ))
                ]

            if not versions:
                raise orm.except_orm(
                    _("Warning!"),
                    _("At least one pricelist has no active version !"),
                )

            res[pricelist.id] = versions[0].id

        return res

    _columns = {
        "active_version_id": fields.function(
            _get_active_version,
            string="Active version",
            type="many2one",
            relation="product.pricelist.version",
        ),
    }

    def action_pricelist_sent(self, cr, uid, ids, context=None):
        # This function opens a window to compose an email,
        # with the pricelist template message loaded by default

        # This option should only be used for a single id at a time.
        assert len(ids) == 1

        ir_model_data = self.pool.get('ir.model.data')
        try:
            template_id = ir_model_data.get_object_reference(
                cr, uid,
                'sale_send_pricelist_by_email',
                'email_template_pricelist')[1]
        except ValueError:
            template_id = False

        try:
            compose_form_id = ir_model_data.get_object_reference(
                cr, uid, 'mail', 'email_compose_message_wizard_form')[1]
        except ValueError:
            compose_form_id = False

        ctx = dict(context)
        ctx.update({
            'default_model': 'product.pricelist',
            'default_res_id': ids[0],
            'default_use_template': bool(template_id),
            'default_template_id': template_id,
            'default_composition_mode': 'comment',
        })
        # Full explanation of this return is here :
        # http://stackoverflow.com/questions/12634031
        return {
            'type': 'ir.actions.act_window',
            'view_type': 'form',
            'view_mode': 'form',
            'res_model': 'mail.compose.message',
            'views': [(compose_form_id, 'form')],
            'view_id': compose_form_id,
            'target': 'new',
            'context': ctx,
        }
