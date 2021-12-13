# Copyright 2021 Tecnativa - Víctor Martínez
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).
from lxml import etree

from odoo.tests import common


class TestSalePartnerSelectableOption(common.SavepointCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()

    def test_sale_order(self):
        result = self.env["sale.order"].fields_view_get(
            view_id=self.env.ref("sale.view_order_form").id, view_type="form",
        )
        doc = etree.XML(result["arch"])
        field = doc.xpath("//field[@name='partner_id']")
        domain = field[0].get("domain")
        self.assertTrue("('sale_selectable', '=', True)" in domain)
