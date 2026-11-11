# Copyright 2026 Camptocamp SA (https://www.camptocamp.com).
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).

from odoo.orm.commands import Command
from odoo.orm.domains import Domain
from odoo.orm.types import ValuesType
from odoo.tests.common import TransactionCase

from odoo.addons.sale.models.sale_order import SaleOrder
from odoo.addons.sale.models.sale_order_line import SaleOrderLine


class TestSaleExceptionLineTooltipCommon(TransactionCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()

        # Other installed modules may ship their own active exception rules: deactivate
        # them so this test suite only ever sees the rules it creates itself
        cls.env["exception.rule"].search(Domain.TRUE).action_archive()

        cls.customer = cls.env["res.partner"].create({"name": "Test customer"})
        cls.product = cls.env["product.product"].create(
            {"name": "Test Product", "type": "consu", "list_price": 100.0}
        )
        cls.exception_rule = cls.env["exception.rule"].create(
            {
                "name": "Product warning",
                "description": "The product has a warning in its form",
                "sequence": 40,
                "model": "sale.order.line",
                "code": "failed = bool(self.product_id.sale_line_warn_msg)",
                "active": False,
            }
        )

    @classmethod
    def _make_sale_order(cls, sale_values: ValuesType | None = None) -> SaleOrder:
        sale_values: ValuesType = dict(sale_values or {})
        if "partner_id" not in sale_values:
            sale_values["partner_id"] = cls.customer.id
        if "order_line" not in sale_values:
            sale_values["order_line"] = [
                Command.create(
                    {
                        "name": cls.product.name,
                        "product_id": cls.product.id,
                        "product_uom_qty": 1,
                        "price_unit": cls.product.list_price,
                    }
                )
            ]
        return cls.env["sale.order"].create([sale_values])

    @classmethod
    def _make_sale_line(
        cls, line_values: list[ValuesType] | ValuesType | None = None
    ) -> SaleOrderLine:
        sale_values: ValuesType = {}
        if line_values:
            if isinstance(line_values, dict):
                line_values = [line_values]
            sale_values["order_line"] = [Command.create(v) for v in line_values]
        return cls._make_sale_order(sale_values).order_line
