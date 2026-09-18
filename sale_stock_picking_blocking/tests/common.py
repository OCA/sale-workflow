# Copyright 2024 ForgeFlow S.L.
#   (http://www.forgeflow.com)
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl.html).

from typing import Any

from odoo.orm.types import ValuesType
from odoo.tests import TransactionCase, new_test_user

# NB: we don't import ``odoo.addons.base.tests.common.BaseCommon`` because we don't
# need its overhead, just the disabled-mail context values
from odoo.addons.base.tests.common import DISABLED_MAIL_CONTEXT


class TestSaleDeliveryBlockSetup(TransactionCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.setUpEnv()
        cls.setUpRecords()

    @classmethod
    def setUpEnv(cls):
        """Prepares the test environment"""
        cls.env = cls.env(**cls._prepare_env_values())

    @classmethod
    def _prepare_env_values(cls) -> dict[str, Any]:
        """Prepares the test environment"""
        return {"context": dict(cls.env.context, **DISABLED_MAIL_CONTEXT)}

    @classmethod
    def setUpRecords(cls):
        cls.setUpTestUsers()
        cls.setUpBlockReasons()
        cls.setUpPartners()
        cls.setUpPaymentTerms()
        cls.setUpProducts()
        cls.setUpSaleOrders()
        cls.setUpSaleOrderLines()

    @classmethod
    def setUpTestUsers(cls):
        """Prepares the test users (1 by default)

        These users can be used to execute tests by decorating the tests themselves
        with ``@odoo.tests.common.users(<user-login-1>, <user-login-2>, ...)``.
        """
        cls.test_users = sum(
            [new_test_user(**v) for v in cls._prepare_new_test_user_kwargs()],
            start=cls.env["res.users"],
        )

    @classmethod
    def _prepare_new_test_user_kwargs(cls) -> list[dict[str, Any]]:
        """Prepares the test users' values (1 by default)

        Beware: these values aren't passed to ``res.users.create()``, but to
        ``odoo.tests.common.new_test_user()`` instead.
        """
        return [
            {
                "env": cls.env,
                "name": "Test User",
                "login": "login@test-user.com",
                "password": "test-user-pswd",
                "email": "email@test-user.com",
                # CRUD access to sales
                # (``new_test_user()`` expects a comma-separated list of XMLIDs)
                "groups": "sales_team.group_sale_manager",
            }
        ]

    @classmethod
    def setUpBlockReasons(cls):
        """Prepares block reasons (3 by default)"""
        cls.block_reasons = cls.env["sale.delivery.block.reason"].create(
            cls._prepare_block_reasons_values()
        )

    @classmethod
    def _prepare_block_reasons_values(cls) -> list[ValuesType]:
        """Prepares block reasons' values (3 by default)"""
        return [{"name": "Block 1"}, {"name": "Block 2"}, {"name": "Block 3"}]

    @classmethod
    def setUpPartners(cls):
        """Prepares partners (3 by default)"""
        cls.partners = cls.env["res.partner"].create(cls._prepare_partners_values())

    @classmethod
    def _prepare_partners_values(cls) -> list[ValuesType]:
        """Prepares partners' values (3 by default)"""
        # The 1st partner isn't assigned to any block reason.
        # The 2nd and 3rd partners are assigned to the 2nd and 3rd block reason.
        return [
            {"name": "Partner 1"},
            {"name": "Partner 2", "default_delivery_block": cls.block_reasons[1].id},
            {"name": "Partner 3", "default_delivery_block": cls.block_reasons[2].id},
        ]

    @classmethod
    def setUpPaymentTerms(cls):
        """Prepares payment terms (3 by default)"""
        cls.payment_terms = cls.env["account.payment.term"].create(
            cls._prepare_payment_terms_values()
        )

    @classmethod
    def _prepare_payment_terms_values(cls) -> list[ValuesType]:
        """Prepares payment terms' values (3 by default)"""
        # The 1st payment term isn't assigned to any block reason.
        # The 2nd and 3rd payment terms are assigned to the 2nd and 3rd block reason.
        return [
            {"name": "PT 1"},
            {
                "name": "PT 2",
                "default_delivery_block_reason_id": cls.block_reasons[1].id,
            },
            {
                "name": "PT 3",
                "default_delivery_block_reason_id": cls.block_reasons[2].id,
            },
        ]

    @classmethod
    def setUpProducts(cls):
        """Prepares products (1 by default)"""
        cls.products = cls.env["product.product"].create(cls._prepare_product_values())

    @classmethod
    def _prepare_product_values(cls) -> list[ValuesType]:
        """Prepares products' values (1 by default)"""
        return [
            {
                "name": "Product",
                "type": "consu",
                "list_price": 100.0,
                "standard_price": 60.0,
                "uom_id": cls.env.ref("uom.product_uom_unit").id,
            }
        ]

    @classmethod
    def setUpSaleOrders(cls):
        """Prepares sale orders (1 by default)"""
        cls.sale_orders = cls.env["sale.order"].create(cls._prepare_sale_order_values())

    @classmethod
    def _prepare_sale_order_values(cls) -> list[ValuesType]:
        """Prepares sale orders' values (1 by default)"""
        return [{"partner_id": cls.partners[0].id}]

    @classmethod
    def setUpSaleOrderLines(cls):
        """Prepares sale order lines (1 by default)"""
        cls.sale_order_lines = cls.env["sale.order.line"].create(
            cls._prepare_sale_order_line_values()
        )

    @classmethod
    def _prepare_sale_order_line_values(cls) -> list[ValuesType]:
        """Prepares sale order lines' values (1 by default)"""
        return [
            {
                "order_id": cls.sale_orders[0].id,
                "product_id": cls.products[0].id,
                "product_uom_qty": 1.0,
            }
        ]
