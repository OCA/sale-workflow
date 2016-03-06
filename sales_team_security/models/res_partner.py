# -*- coding: utf-8 -*-
# © 2016 Pedro M. Baeza <pedro.baeza@serviciosbaeza.com>
# License AGPL-3 - See http://www.gnu.org/licenses/agpl-3.0.html

from openerp import api, models
from lxml import etree


class ResPartner(models.Model):
    _inherit = 'res.partner'

    @api.model
    def fields_view_get(self, view_id=None, view_type='form', toolbar=False,
                        submenu=False):
        """Patch view to inject the default value for the section_id."""
        res = super(ResPartner, self).fields_view_get(
            view_id=view_id, view_type=view_type, toolbar=toolbar,
            submenu=submenu)
        if view_type == 'form':
            eview = etree.fromstring(res['arch'])
            xml_fields = eview.xpath("//field[@name='child_ids']")
            if xml_fields:
                context_str = xml_fields[0].get('context', '{}')
                context_str = (
                    context_str[:1] + "'default_section_id': section_id, " +
                    context_str[1:])
                xml_fields[0].set('context', context_str)
            res['arch'] = etree.tostring(eview)
        return res

    @api.multi
    def onchange_address(self, use_parent_address, parent_id):
        res = super(ResPartner, self).onchange_address(
            use_parent_address, parent_id)
        if parent_id:
            parent = self.browse(parent_id)
            if parent.section_id:
                value = res.setdefault('value', {})
                value['section_id'] = parent.section_id.id
        return res
