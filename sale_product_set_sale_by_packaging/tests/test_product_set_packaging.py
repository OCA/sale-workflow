# Copyright 2021 Camptocamp SA
# @author Simone Orsi <simone.orsi@camptocamp.com>
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl)

from odoo import exceptions
from odoo.tests import common


class TestProductSetPackaging(common.SavepointCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.env = cls.env(context=dict(cls.env.context, tracking_disable=True))
        cls.line = cls.env.ref("sale_product_set.product_set_line_computer_3")
        cls.packaging = cls.env["product.packaging"].create(
            {"name": "Box", "product_id": cls.line.product_id.id, "qty": 10}
        )
        cls.line.product_packaging_id = cls.packaging
        cls.tmpl = cls.line.product_id.product_tmpl_id

    def test_sell_only_by_packaging_ko(self):
        self.line.product_id.sell_only_by_packaging = True
        with self.assertRaisesRegex(
            exceptions.UserError, "can be sold only by packaging"
        ):
            self.line.product_packaging_id = False

    def test_sell_only_by_packaging_ok(self):
        self.line.product_id.sell_only_by_packaging = False
        self.line.product_packaging_id = False

    def test_product_set_to_check(self):
        self.assertFalse(self.line.product_id.sell_only_by_packaging_prod_set_tocheck)
        self.line.product_packaging_id = False
        self.tmpl.sell_only_by_packaging = True
        self.assertTrue(self.line.product_id.sell_only_by_packaging_prod_set_tocheck)

    def test_tmpl_action(self):
        action = self.tmpl.action_view_product_set_lines_to_check()
        self.assertEqual(action["domain"], [("product_id", "in", [])])
        self.line.product_packaging_id = False
        self.tmpl.sell_only_by_packaging = True
        action = self.tmpl.action_view_product_set_lines_to_check()
        self.assertEqual(
            action["domain"], [("product_id", "in", [self.line.product_id.id])]
        )

    def test_prod_action(self):
        action = self.line.product_id.action_view_product_set_lines_to_check()
        self.assertEqual(action["domain"], [("product_id", "in", [])])
        self.line.product_packaging_id = False
        self.tmpl.sell_only_by_packaging = True
        action = self.line.product_id.action_view_product_set_lines_to_check()
        self.assertEqual(
            action["domain"], [("product_id", "in", [self.line.product_id.id])]
        )
