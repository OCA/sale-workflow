# Copyright 2018 Tecnativa - Sergio Teruel
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).
from lxml import etree

from odoo import api, fields, models


class SaleOrder(models.Model):
    _inherit = "sale.order"

    general_discount = fields.Float(
        string="Discount (%)",
        compute="_compute_general_discount",
        store=True,
        readonly=False,
        digits="Discount",
    )

    @api.depends("partner_id")
    def _compute_general_discount(self):
        for so in self:
            so.general_discount = so.partner_id.sale_discount

    @api.model
    def fields_view_get(
        self, view_id=None, view_type="form", toolbar=False, submenu=False
    ):
        """The purpose of this is to write a context on "order_line" field
        respecting other contexts on this field.
        There is a PR (https://github.com/odoo/odoo/pull/26607) to odoo for
        avoiding this. If merged, remove this method and add the attribute
        in the field.
        """
        res = super(SaleOrder, self).fields_view_get(
            view_id=view_id,
            view_type=view_type,
            toolbar=toolbar,
            submenu=submenu,
        )
        if view_type == "form":
            order_xml = etree.XML(res["arch"])
            order_line_fields = order_xml.xpath("//field[@name='order_line']")
            if order_line_fields:
                order_line_field = order_line_fields[0]
                context = order_line_field.attrib.get("context", "{}").replace(
                    "{",
                    "{'default_discount': general_discount, ",
                    1,
                )
                order_line_field.attrib["context"] = context
                res["arch"] = etree.tostring(order_xml)
        return res
