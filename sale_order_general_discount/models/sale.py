# Copyright 2018 Tecnativa - Sergio Teruel
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).
from odoo import api, fields, models
from odoo.addons import decimal_precision as dp
from lxml import etree


class SaleOrder(models.Model):
    _inherit = 'sale.order'

    general_discount = fields.Float(
        digits=dp.get_precision('Discount'),
        string='Discount (%)',
    )

    @api.onchange('partner_id')
    def onchange_partner_id(self):
        super().onchange_partner_id()
        self.general_discount = self.partner_id.sale_discount

    @api.onchange('general_discount')
    def onchange_general_discount(self):
        self.mapped('order_line').update({
            'discount': self.general_discount,
        })

    @api.model
    def fields_view_get(self, view_id=None, view_type='form', toolbar=False,
                        submenu=False):
        """The purpose of this is write a context on order_line field
         respecting other contexts on this field.
         There is PR (https://github.com/odoo/odoo/pull/26607) to odoo for
         avoid this, only update field in xml view and remove this method"""
        res = super(SaleOrder, self).fields_view_get(
            view_id, view_type, toolbar, submenu)
        if view_type == 'form':
            order_xml = etree.XML(res['arch'])
            order_line_path = "//field[@name='order_line']"
            order_line_fields = order_xml.xpath(order_line_path)
            if order_line_fields:
                order_line_field = order_line_fields[0]
                context = order_line_field.attrib.get("context", "{}")
                context = context.replace(
                    "{",
                    "{'default_discount': general_discount, ", 1)
                order_line_field.attrib['context'] = context
                res['arch'] = etree.tostring(order_xml)
        return res
