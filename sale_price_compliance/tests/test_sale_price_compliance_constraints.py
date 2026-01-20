# Copyright 2026 Moduon Team S.L.
# License LGPL-3.0 or later (https://www.gnu.org/licenses/lgpl-3.0)

from psycopg2 import IntegrityError

from odoo.tests.common import TransactionCase, tagged
from odoo.tools import mute_logger


@tagged("post_install", "-at_install")
class TestPriceComplianceConstraints(TransactionCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        # Create a clean company for testing
        cls.company = cls.env["res.company"].create(
            {
                "name": "Test Company SQL Constraints",
            }
        )

    def test_valid_cases(self):
        """Success Case: Positive values and no gaps."""
        # Case 1: All values are zero [0, 0, 0]
        self.company.write(
            {
                "use_price_compliance_threshold": True,
                "price_compliance_threshold_t1": 0.0,
                "price_compliance_threshold_t2": 0.0,
                "price_compliance_threshold_t3": 0.0,
            }
        )
        # Case 2: T1 has value, others are zero (No gaps) [10%, 0%, 0%]
        self.company.write({"price_compliance_threshold_t1": 0.1})
        # Case 3: T1 and T2 have values (No gaps) [10%, 5%, 0%]
        self.company.write({"price_compliance_threshold_t2": 0.05})
        # Case 4: T1 and T2 and T3 have values (No gaps) [10%, 5%, 1%]
        self.company.write({"price_compliance_threshold_t3": 0.01})

    @mute_logger("odoo.sql_db")
    def test_constraint_positive(self):
        """Expected Failure: Negative numbers are not allowed if use thresholds."""
        with self.assertRaises(IntegrityError):
            self.company.write(
                {
                    "use_price_compliance_threshold": True,
                    "price_compliance_threshold_t1": -0.05,  # Negative value
                    "price_compliance_threshold_t2": 0.0,
                    "price_compliance_threshold_t3": 0.0,
                }
            )

    @mute_logger("odoo.sql_db")
    def test_constraint_le_1(self):
        """Expected Failure: High numbers are not allowed if use thresholds."""
        with self.assertRaises(IntegrityError):
            self.company.write(
                {
                    "use_price_compliance_threshold": True,
                    "price_compliance_threshold_t1": 1.01,  # > 1.0 value
                    "price_compliance_threshold_t2": 0.0,
                    "price_compliance_threshold_t3": 0.0,
                }
            )

    @mute_logger("odoo.sql_db")
    def test_constraint_gaps_start(self):
        """Expected Failure: Gap at the beginning (T1=0, T2>0)."""
        with self.assertRaises(IntegrityError):
            self.company.write(
                {
                    "use_price_compliance_threshold": True,
                    "price_compliance_threshold_t1": 0.0,  # Gap here
                    "price_compliance_threshold_t2": 0.05,
                    "price_compliance_threshold_t3": 0.0,
                }
            )

    @mute_logger("odoo.sql_db")
    def test_constraint_gaps_middle(self):
        """Expected Failure: Gap in the middle (T2=0, T3>0)."""
        with self.assertRaises(IntegrityError):
            self.company.write(
                {
                    "use_price_compliance_threshold": True,
                    "price_compliance_threshold_t1": 0.1,
                    "price_compliance_threshold_t2": 0.0,  # Gap here
                    "price_compliance_threshold_t3": 0.05,
                }
            )

    def test_ignore_constraint_if_disabled(self):
        """Success Case: If the check is disabled, allow anything."""
        # Even with negatives or gaps, if 'use_...' is False, it should save
        self.company.write(
            {
                "use_price_compliance_threshold": False,
                "price_compliance_threshold_t1": -0.1,  # Negative
                "price_compliance_threshold_t2": 0.0,
                "price_compliance_threshold_t3": 0.05,  # Gap
            }
        )

    def test_default_texts_parameter(self):
        """Check if default texts are used if parameter is not set."""
        # Set custom texts
        selection_texts = self.env[
            "sale.order.line"
        ]._get_price_compliance_selection_tiers_text()
        default_texts = self.env[
            "sale.order.line"
        ]._get_price_compliance_selection_tiers_text_default()
        self.assertEqual(selection_texts[0][1], default_texts[0][1])
        self.assertEqual(selection_texts[1][1], default_texts[1][1])
        self.assertEqual(selection_texts[2][1], default_texts[2][1])
        self.assertEqual(selection_texts[3][1], default_texts[3][1])
        self.assertEqual(selection_texts[4][1], default_texts[4][1])

    def test_custom_texts_parameter(self):
        """Check if custom texts are used if parameter is set."""
        # Set custom texts
        self.env["ir.config_parameter"].sudo().set_param(
            "sale_price_compliance.price_compliance_selection_tiers_text",
            "{'t1': 'T. Gold', 't2': 'T. Silver', 'pricelist': 'T. Agreeed Price'}",
        )
        selection_texts = self.env[
            "sale.order.line"
        ]._get_price_compliance_selection_tiers_text()
        default_texts = self.env[
            "sale.order.line"
        ]._get_price_compliance_selection_tiers_text_default()
        self.assertEqual(selection_texts[0][1], "T. Gold")
        self.assertEqual(selection_texts[1][1], "T. Silver")
        self.assertEqual(selection_texts[2][1], default_texts[2][1])
        self.assertEqual(selection_texts[3][1], default_texts[3][1])
        self.assertEqual(selection_texts[4][1], "T. Agreeed Price")

    def test_custom_icons_parameter(self):
        """Check if custom icons are used if parameter is set."""
        # Set custom icons
        self.env["ir.config_parameter"].sudo().set_param(
            "sale_price_compliance.price_compliance_selection_tiers_icon",
            "{'t1': '🟢', 't2': '🟡', 't3': '🟠', 'pricelist': '🟣'}",
        )
        selection_icons = self.env[
            "sale.order.line"
        ]._get_price_compliance_selection_tiers_icon_color()
        default_icons = self.env[
            "sale.order.line"
        ]._get_price_compliance_selection_tiers_icon_color_default()
        self.assertEqual(selection_icons[0][1], "🟢")
        self.assertEqual(selection_icons[1][1], "🟡")
        self.assertEqual(selection_icons[2][1], "🟠")
        self.assertEqual(selection_icons[3][1], default_icons[3][1])
        self.assertEqual(selection_icons[4][1], "🟣")

    def test_custom_texts_wrong_parameter(self):
        """Check if custom texts are used if parameter is not correctly set."""
        # Set custom texts
        self.env["ir.config_parameter"].sudo().set_param(
            "sale_price_compliance.price_compliance_selection_tiers_text",
            "test wrong parameter",
        )
        selection_texts = self.env[
            "sale.order.line"
        ]._get_price_compliance_selection_tiers_text()
        default_texts = self.env[
            "sale.order.line"
        ]._get_price_compliance_selection_tiers_text_default()
        self.assertEqual(selection_texts[0][1], default_texts[0][1])
        self.assertEqual(selection_texts[1][1], default_texts[1][1])
        self.assertEqual(selection_texts[2][1], default_texts[2][1])
        self.assertEqual(selection_texts[3][1], default_texts[3][1])
        self.assertEqual(selection_texts[4][1], default_texts[4][1])
