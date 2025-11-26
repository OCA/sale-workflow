# Copyright 2023 ACSONE SA/NV
# Copyright 2025 Michael Tietz (MT Software) <mtietz@mt-software.de>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo import Command
from odoo.tests.common import TransactionCase


class TestSaleOrderLineCancelBase(TransactionCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.partner = cls.env["res.partner"].create({"name": "Partner"})
        cls.product_1 = cls._create_product()
        cls.sale = cls._add_done_sale_order()
        cls.wiz = cls.env["sale.order.line.cancel"].create({})

    @classmethod
    def _prepare_product_vals(cls):
        return {
            "name": "test product 1",
            "sale_ok": True,
            "active": True,
        }

    @classmethod
    def _create_product(cls):
        return cls.env["product.product"].create(cls._prepare_product_vals())

    @classmethod
    def _prepare_sale_order_values(cls, **kwargs):
        lines = [
            Command.create(
                {
                    "name": cls.product_1.name,
                    "product_id": cls.product_1.id,
                    "product_uom_qty": 10,
                    "product_uom": cls.product_1.uom_id.id,
                    "price_unit": 1,
                }
            )
        ]
        so_values = {
            "partner_id": cls.partner.id,
            "order_line": lines,
        }
        if kwargs:
            so_values.update(kwargs)
        return so_values

    @classmethod
    def _create_sale_order(cls, **kwargs):
        sale_order_model = cls.env["sale.order"]
        so_values = cls._prepare_sale_order_values(**kwargs)
        return sale_order_model.create(so_values)

    @classmethod
    def _add_done_sale_order(cls, **kwargs):
        so = cls._create_sale_order(**kwargs)
        so.action_confirm()
        so.action_done()
        return so
