# Copyright 2026 Studio73 - Pablo Cortés <pablo.cortes@studio73.es>
# Copyright 2017 Tecnativa - David Vidal
# Copyright 2018 Simone Rubino - Agile Business Group
# Copyright 2022 Manuel Regidor - Sygel Technology
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo.addons.base.tests.common import BaseCommon


class SaleTripleDiscountCommon(BaseCommon):
    @classmethod
    def setUpClass(cls) -> None:
        super().setUpClass()
        cls.env.user.group_ids += cls.env.ref("sale.group_discount_per_so_line")
        cls.partner = cls.env["res.partner"].create({"name": "Mr. Odoo"})
        cls.product1 = cls.env["product.product"].create(
            {"name": "Test Product 1", "type": "service", "invoice_policy": "order"}
        )
        cls.product2 = cls.env["product.product"].create(
            {"name": "Test Product 2", "type": "service", "invoice_policy": "order"}
        )
        cls.tax = cls.env["account.tax"].create(
            {
                "name": "TAX 15%",
                "amount_type": "percent",
                "type_tax_use": "sale",
                "amount": 15.0,
            }
        )
        cls.order = cls.env["sale.order"].create({"partner_id": cls.partner.id})
        sale_order_line = cls.env["sale.order.line"]
        cls.so_line1 = sale_order_line.create(
            {
                "order_id": cls.order.id,
                "product_id": cls.product1.id,
                "name": "Line 1",
                "product_uom_qty": 1.0,
                "tax_ids": [(6, 0, [cls.tax.id])],
                "price_unit": 600.0,
            }
        )
        cls.so_line2 = sale_order_line.create(
            {
                "order_id": cls.order.id,
                "product_id": cls.product2.id,
                "name": "Line 2",
                "product_uom_qty": 10.0,
                "tax_ids": [(6, 0, [cls.tax.id])],
                "price_unit": 60.0,
            }
        )
