# Copyright 2026 ACSONE SA/NV
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).
from odoo.addons.base.tests.common import BaseCommon


class TestSalePackaging(BaseCommon):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.product = cls.env["product.product"].create(
            {
                "name": "Product 1",
            }
        )
        cls.packaging = cls.env["product.packaging"].create(
            {
                "name": "Box 1",
                "product_id": cls.product.id,
            }
        )
