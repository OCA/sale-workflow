# Copyright 2026 Lorenzo Carta - Innovyou
# License LGPL-3.0 or later (https://www.gnu.org/licenses/lgpl).
from odoo.fields import Command

from odoo.addons.account.tests.common import AccountTestInvoicingCommon
from odoo.addons.sale.tests.common import SaleCommon


class SaleMultiDiscountCommon(AccountTestInvoicingCommon, SaleCommon):
    """Base test class for ``sale_multi_discount``.

    Combines ``AccountTestInvoicingCommon`` (for chart of accounts and
    journals required by SO -> invoice tests) with ``SaleCommon`` (for
    partners, products and pricelist fixtures).
    """

    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls._enable_discounts()

    @classmethod
    def _make_order(cls, *, lines=None):
        """Create a one-line sale order on ``cls.product``."""
        lines = (
            lines
            if lines is not None
            else [
                Command.create(
                    {
                        "product_id": cls.product.id,
                        "product_uom_qty": 1.0,
                    }
                )
            ]
        )
        return cls.env["sale.order"].create(
            {
                "partner_id": cls.partner.id,
                "order_line": lines,
            }
        )
