# Copyright 2026 - TODAY, Kaynnan Lemes <kaynnan.lemes@escodoo.com.br>

import datetime

from odoo.tests.common import TransactionCase


class BlanketOrderCase(TransactionCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.partner = cls.env["res.partner"].create({"name": "Test Partner"})
        cls.product = cls.env["product.product"].create(
            {"name": "Test Product", "type": "consu", "standard_price": 50.0}
        )
        cls.service = cls.env["product.product"].create(
            {"name": "Test Service", "type": "service", "standard_price": 80.0}
        )
        cls.pricelist = cls.env["product.pricelist"].search([], limit=1)

    def _create_blanket_order(self, **kwargs):
        defaults = {
            "partner_id": self.partner.id,
            "pricelist_id": self.pricelist.id,
            "validity_date": datetime.date.today() + datetime.timedelta(days=365),
        }
        defaults.update(kwargs)
        return self.env["sale.blanket.order"].create(defaults)

    def _add_line_to_order(self, order, product=None, qty=10.0, price=100.0):
        if product is None:
            product = self.product
        return self.env["sale.blanket.order.line"].create(
            {
                "order_id": order.id,
                "product_id": product.id,
                "product_uom": product.uom_id.id,
                "original_uom_qty": qty,
                "price_unit": price,
            }
        )

    def _create_fake_invoiced_scenario(self, blanket_order):
        sale_order = self.env["sale.order"].create(
            {
                "partner_id": blanket_order.partner_id.id,
                "state": "sale",
            }
        )
        self.env["sale.order.line"].create(
            {
                "order_id": sale_order.id,
                "blanket_line_id": blanket_order.line_ids[0].id,
                "product_id": blanket_order.line_ids[0].product_id.id,
                "product_uom_qty": blanket_order.line_ids[0].original_uom_qty,
                "price_unit": blanket_order.line_ids[0].price_unit,
            }
        )
        sale_order.write({"invoice_status": "invoiced"})
