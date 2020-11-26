# Copyright 2020 Camptocamp SA
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).
from odoo.tests.common import SavepointCase


class TestSaleCouponMultiCurrencyCommon(SavepointCase):
    """Common class for multi currency program tests."""

    @classmethod
    def setUpClass(cls):
        """Set up common data for multi currency coupon tests."""
        super().setUpClass()
        # Records.
        # Coupon Programs.
        cls.program_coupon_percentage = cls.env.ref("sale_coupon.10_percent_coupon")
        # Currencies.
        cls.company_main = cls.env.ref("base.main_company")
        cls.currency_company = cls.company_main.currency_id
        cls.usd = cls.env.ref("base.USD")
        cls.eur = cls.env.ref("base.EUR")
        # Depending on modules installed, company currency can be
        # different, so we set other currency, the one that is not
        # set on company currency.
        cls.currency_other = cls.usd if cls.currency_company != cls.usd else cls.eur
