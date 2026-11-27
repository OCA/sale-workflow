# Copyright 2026 ForgeFlow S.L.
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

import ast

from lxml import etree

from odoo.tests import TransactionCase, tagged


@tagged("post_install", "-at_install")
class TestSalePartnerDisplayRef(TransactionCase):
    """The Sales views must inject ``partner_display_ref_field='ref'`` into the
    customer ``partner_id`` field context. The decoration mechanism itself is
    covered by the ``partner_display_ref`` base module's tests.
    """

    def _assert_partner_display_ref_field(self, xmlid):
        view = self.env.ref(xmlid)
        tree = etree.fromstring(view.get_combined_arch())
        partner_fields = tree.xpath("//field[@name='partner_id']")
        self.assertTrue(partner_fields, f"{xmlid} must contain a partner_id field")
        contexts = [
            ast.literal_eval(field.get("context"))
            for field in partner_fields
            if field.get("context")
        ]
        self.assertTrue(
            any(ctx.get("partner_display_ref_field") == "ref" for ctx in contexts),
            f"{xmlid} must inject partner_display_ref_field='ref' into the "
            f"partner_id context",
        )

    def test_order_form_injects_context(self):
        self._assert_partner_display_ref_field("sale.view_order_form")

    def test_quotation_tree_injects_context(self):
        self._assert_partner_display_ref_field("sale.view_quotation_tree")

    def test_sales_order_filter_injects_context(self):
        self._assert_partner_display_ref_field("sale.view_sales_order_filter")
