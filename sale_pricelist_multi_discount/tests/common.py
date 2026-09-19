# Copyright 2026 Lorenzo Carta - Innovyou
# License LGPL-3.0 or later (https://www.gnu.org/licenses/lgpl).
from odoo import SUPERUSER_ID
from odoo.fields import Command

from odoo.addons.account.tests.common import AccountTestInvoicingCommon
from odoo.addons.sale.tests.common import SaleCommon


class SalePricelistMultiDiscountCommon(AccountTestInvoicingCommon, SaleCommon):
    """Base test class for ``sale_pricelist_multi_discount``.

    Mirrors the setup from the upstream modules: chart of accounts via
    ``AccountTestInvoicingCommon`` and product / pricelist fixtures via
    ``SaleCommon``. The ``sale.group_discount_per_so_line`` group is also
    granted to SUPERUSER so that ``_is_discount_feature_enabled`` returns
    ``True`` and the SOL distribution compute actually seeds from the
    pricelist.
    """

    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.env["res.users"].browse(SUPERUSER_ID).groups_id |= cls.env.ref(
            "sale.group_discount_per_so_line"
        )
        cls._enable_discounts()
        cls._enable_pricelists()

    # ------------------------------------------------------------------
    # Helpers
    # ------------------------------------------------------------------

    @classmethod
    def _make_rule(
        cls,
        *,
        percent=0.0,
        distribution=None,
        pricelist=None,
        product=None,
        compute_price="percentage",
    ):
        """Create a pricelist rule on the given product."""
        pricelist = pricelist or cls.pricelist
        product = product or cls.product
        vals = {
            "pricelist_id": pricelist.id,
            "applied_on": "1_product",
            "product_tmpl_id": product.product_tmpl_id.id,
            "compute_price": compute_price,
        }
        # ``distribution`` is the single source of truth. When it is not
        # given, a plain ``percent_price`` is written so its inverse seeds the
        # distribution, mirroring how a user edits a single-value rule.
        if distribution is not None:
            vals["discount_distribution"] = distribution
        else:
            vals["percent_price"] = percent
        return cls.env["product.pricelist.item"].create(vals)

    @classmethod
    def _make_order_on_product(cls, product=None, pricelist=None):
        product = product or cls.product
        pricelist = pricelist if pricelist is not None else cls.pricelist
        return cls.env["sale.order"].create(
            {
                "partner_id": cls.partner.id,
                "pricelist_id": pricelist.id if pricelist else False,
                "order_line": [
                    Command.create(
                        {
                            "product_id": product.id,
                            "product_uom_qty": 1.0,
                        }
                    )
                ],
            }
        )
