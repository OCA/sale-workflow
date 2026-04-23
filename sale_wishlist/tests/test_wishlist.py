# Copyright 2019 Camptocamp SA
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).
from odoo.addons.base.tests.common import BaseCommon


class TestWishlist(BaseCommon):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.sale_order = cls.env["sale.order"]
        cls.product_set = cls.env["product.set"]
        cls.partner2 = cls.env["res.partner"].create({"name": "Test Partner 2"})
        cls.product_set_services = cls.env["product.set"].create(
            {"name": "Services", "ref": "Services"}
        )

    def test_wishlist_count_no_typology_match(self):
        prod_set = self.product_set_services
        for __ in range(2):
            prod_set.copy(default={"partner_id": self.partner.id})
        for __ in range(4):
            prod_set.copy(default={"partner_id": self.partner2.id})
        self.assertEqual(self.partner.wishlists_count, 0)
        self.assertEqual(self.partner2.wishlists_count, 0)

    def test_wishlist_count(self):
        prod_set = self.product_set_services
        vals = {"partner_id": self.partner.id, "typology": "wishlist"}
        for __ in range(2):
            prod_set.copy(default=vals)
        vals = {"partner_id": self.partner2.id, "typology": "wishlist"}
        for __ in range(4):
            prod_set.copy(default=vals)
        self.assertEqual(self.partner.wishlists_count, 2)
        self.assertEqual(self.partner2.wishlists_count, 4)

    def test_action(self):
        action = self.partner.action_view_wishlists()
        self.assertEqual(
            action["context"],
            {"default_partner_id": self.partner.id, "default_typology": "wishlist"},
        )
        self.assertEqual(
            action["domain"],
            [("partner_id", "in", [self.partner.id]), ("typology", "=", "wishlist")],
        )
        action = self.partner2.action_view_wishlists()
        self.assertEqual(
            action["context"],
            {"default_partner_id": self.partner2.id, "default_typology": "wishlist"},
        )
        self.assertEqual(
            action["domain"],
            [("partner_id", "in", [self.partner2.id]), ("typology", "=", "wishlist")],
        )
