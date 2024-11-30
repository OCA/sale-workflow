# Copyright 2020 Camptocamp SA
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl)

from odoo.addons.product_packaging_level_salable.tests.common import Common

TU_PRODUCT_QTY = 20
PL_PRODUCT_QTY = TU_PRODUCT_QTY * 30


class SellOnlyByPackagingCommon(Common):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.env.user.groups_id += cls.env.ref("product.group_stock_packaging")
