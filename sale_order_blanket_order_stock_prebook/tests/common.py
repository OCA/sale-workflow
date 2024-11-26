# Copyright 2024 ACSONE SA/NV
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).


from odoo.addons.sale_order_blanket_order.tests import common


class SaleOrderBlanketOrderCase(common.SaleOrderBlanketOrderCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.blanket_so.blanket_reservation_strategy = "at_confirm"
