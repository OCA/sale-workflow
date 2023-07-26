# Copyright 2023 Jarsa
# License LGPL-3.0 or later (https://www.gnu.org/licenses/lgpl).

from odoo.exceptions import ValidationError
from odoo.tests.common import Form, TransactionCase


class TestResPartner(TransactionCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.pricelist_1 = cls.env["product.pricelist"].create(
            {
                "name": "Pricelist 1",
            }
        )

        cls.pricelist_2 = cls.env["product.pricelist"].create(
            {
                "name": "Pricelist 2",
            }
        )

        cls.partner = cls.env["res.partner"].create(
            {
                "name": "Example",
                "property_product_pricelist": cls.pricelist_1.id,
                "allowed_pricelist_ids": [(4, cls.pricelist_1.id)],
            }
        )
        cls.env.company.use_partner_pricelist = True

    def test_01_partner_constraint(self):
        with self.assertRaisesRegex(
            ValidationError,
            "The selected Pricelist is not allowed for this Partner. "
            "Please select one of the allowed pricelists.",
        ):
            self.partner.property_product_pricelist = self.pricelist_2

    def test_02_sale_order_constraint(self):
        order = Form(self.env["sale.order"])
        order.partner_id = self.partner
        order.pricelist_id = self.pricelist_2
        with self.assertRaisesRegex(
            ValidationError, "The selected Pricelist is not allowed for this Partner."
        ):
            order.save()
