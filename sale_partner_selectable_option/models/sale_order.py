# Copyright 2021 Tecnativa - Víctor Martínez
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).
from lxml import etree

from odoo import api, models


class SaleOrder(models.Model):
    _inherit = "sale.order"

    @api.model
    def get_view(self, view_id=None, view_type="form", **options):
        res = super().get_view(view_id, view_type, **options)
        if view_type == "form":
            order_xml = etree.XML(res["arch"])
            partner_id_fields = order_xml.xpath("//field[@name='partner_id']")
            if partner_id_fields:
                partner_id_field = partner_id_fields[0]
                domain = partner_id_field.get("domain", "[]").replace(
                    "[", "[('sale_selectable', '=', True),"
                )
                partner_id_field.attrib["domain"] = domain
                res["arch"] = etree.tostring(order_xml)
        return res
