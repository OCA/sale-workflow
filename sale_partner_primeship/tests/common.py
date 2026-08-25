# Copyright 2024 Akretion - Olivier Nibart
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo.addons.base.tests.common import BaseCommon


class TestCommon(BaseCommon):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.SalePrimeship = cls.env["sale.primeship"]
        cls.SaleOrderLine = cls.env["sale.order.line"]
        cls.Partner = cls.env["res.partner"]
        cls.product = cls.env["product.template"].create(
            {
                "name": "Primeship Product",
                "primeship_activation": True,
                "primeship_duration": 6,
            }
        )
        cls.order = (
            cls.env["sale.order"]
            .with_context(disable_cancel_warning=True)
            .create(
                {
                    "partner_id": cls.partner.id,
                }
            )
        )

    def make_primeship(self, start_date, end_date, order_line_id=None):
        return self.SalePrimeship.create(
            {
                "partner_id": self.partner.id,
                "start_date": start_date,
                "end_date": end_date,
                "order_line_id": order_line_id.id if order_line_id else False,
            }
        )

    def make_order_line(self):
        return self.SaleOrderLine.create(
            {
                "order_id": self.order.id,
                "product_id": self.product.product_variant_id.id,
                "product_uom_qty": 1,
            }
        )
