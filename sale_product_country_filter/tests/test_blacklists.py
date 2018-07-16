# -*- coding: utf-8 -*-
# Copyright 2018 ACSONE SA/NV
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo.addons.sale.tests.test_sale_common import TestSale
from odoo.exceptions import ValidationError


class TestBlacklists(TestSale):

    def setUp(self):
        super(TestBlacklists, self).setUp()

    def test_global_flag(self):
        uom_unit = self.env.ref("product.product_uom_unit")
        with self.assertRaises(ValidationError):
            self.env["product.product"].create(
                {
                    "name": "Work",
                    "type": "service",
                    "uom_id": uom_unit.id,
                    "uom_po_id": uom_unit.id,
                }
            )

    def _create_sale_order(self, product):
        return self.env["sale.order"].create(
            {
                "partner_id": self.partner.id,
                "partner_invoice_id": self.partner.id,
                "partner_shipping_id": self.partner.id,
                "order_line": [
                    (
                        0,
                        0,
                        {
                            "name": product.name,
                            "product_id": product.id,
                            "product_uom_qty": 2,
                            "product_uom": product.uom_id.id,
                            "price_unit": 55.0,
                        },
                    )
                ],
                "pricelist_id": self.env.ref("product.list0").id,
            }
        )

    def test_template_blacklist(self):
        uom_unit = self.env.ref("product.product_uom_unit")
        blacklisted_country = self.env.ref("base.pt")
        product = self.env["product.product"].create(
            {
                "name": "Work",
                "type": "service",
                "uom_id": uom_unit.id,
                "uom_po_id": uom_unit.id,
                "tmpl_blacklisted_countries_ids": [
                    (4, blacklisted_country.id)
                ],
            }
        )
        self.partner.write({"country_id": blacklisted_country.id})
        so = self._create_sale_order(product)
        with self.assertRaises(ValidationError):
            so.action_confirm()

    def test_template_no_blacklist(self):
        uom_unit = self.env.ref("product.product_uom_unit")
        blacklisted_country = self.env.ref("base.pt")
        product = self.env["product.product"].create(
            {
                "name": "Work",
                "type": "service",
                "uom_id": uom_unit.id,
                "uom_po_id": uom_unit.id,
                "tmpl_blacklisted_countries_ids": [
                    (4, blacklisted_country.id)
                ],
                "tmpl_globally_allowed": True,
            }
        )
        self.partner.write({"country_id": blacklisted_country.id})
        so = self._create_sale_order(product)
        # should NOT raise
        so.action_confirm()

    def test_category_blacklist(self):
        uom_unit = self.env.ref("product.product_uom_unit")
        blacklisted_country = self.env.ref("base.pt")
        # blacklist country in parent category
        self.env.ref("product.product_category_all").write(
            {"blacklisted_countries_ids": [(4, blacklisted_country.id)]}
        )
        product = self.env["product.product"].create(
            {
                "name": "Work",
                "type": "service",
                "uom_id": uom_unit.id,
                "uom_po_id": uom_unit.id,
                "tmpl_globally_allowed": True,
                "categ_id": self.env.ref("product.product_category_3").id,
            }
        )
        self.partner.write({"country_id": blacklisted_country.id})
        so = self._create_sale_order(product)
        with self.assertRaises(ValidationError):
            so.action_confirm()
