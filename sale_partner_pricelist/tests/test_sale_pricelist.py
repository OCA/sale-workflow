# Copyright 2023 Jarsa
# License LGPL-3.0 or later (https://www.gnu.org/licenses/lgpl).

from odoo.exceptions import ValidationError
from odoo.tests.common import TransactionCase


class TestResPartner(TransactionCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.partner = cls.env["res.partner"].create(
            {
                "name": "Example",
                "property_product_pricelist": cls.env.ref("product.list0").id,
                "allowed_pricelist_ids": [(6, 0, cls.env.ref("product.list0").ids)],
            }
        )

    def test_01_partner_constraint(self):
        different_pricelist = self.env["product.pricelist"].create(
            {
                "name": "New Pricelist",
            }
        )
        with self.assertRaisesRegex(
            ValidationError, "The selected Pricelist is not allowed for this Partner."
        ):
            self.partner.with_context(
                test_enable=True
            ).property_product_pricelist = different_pricelist
        self.partner.write(
            {
                "allowed_pricelist_ids": [(4, different_pricelist.id)],
            }
        )
        self.partner.with_context(
            test_enable=True
        ).property_product_pricelist = different_pricelist
