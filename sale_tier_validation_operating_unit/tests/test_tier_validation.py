# Copyright 2026 CIT Services
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).

from odoo.addons.sale_tier_validation.tests.test_tier_validation import (
    TestSaleTierValidation,
)

ORIG_SETUP_CLASS = TestSaleTierValidation.setUpClass


@classmethod
def _patched_setUpClass(cls):
    ORIG_SETUP_CLASS()
    # sale_operating_unit adds an operating_unit_id to sale.order via a
    # computed field and enforces it via a record rule. Assign all
    # company OUs to test_user_1 so validate_tier() can read the order.
    ous = cls.env["operating.unit"].search([("company_id", "=", cls.env.company.id)])
    cls.test_user_1.operating_unit_ids = [(6, 0, ous.ids)]


TestSaleTierValidation.setUpClass = _patched_setUpClass
