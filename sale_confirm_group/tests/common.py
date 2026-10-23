# Copyright 2025 Camptocamp SA
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl)

from odoo.tests.common import new_test_user

from odoo.addons.base.tests.common import DISABLED_MAIL_CONTEXT
from odoo.addons.sale.tests.common import TestSaleCommonBase


class TestSaleConfirmGroupCommon(TestSaleCommonBase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        # Update context env
        cls.env = cls.env(context=dict(cls.env.context, **DISABLED_MAIL_CONTEXT))

        # Prepare groups
        cls.group_sale_user_xmlid = "sales_team.group_sale_salesman"
        cls.group_sale_user = cls.env.ref(cls.group_sale_user_xmlid)
        cls.group_sale_admin_xmlid = "sales_team.group_sale_manager"
        cls.group_sale_admin = cls.env.ref(cls.group_sale_admin_xmlid)

        # Prepare a test user with "Sales / User: Own Documents Only" group
        cls.test_user = new_test_user(
            cls.env,
            login="test-sale-confirm-group-user",
            groups=cls.group_sale_user_xmlid,
        )

        # Setup company: activate the feature, add "Sales / Administrator" as the only
        # group allowed to confirm sales
        cls.env.company.use_sale_confirmation_groups = True
        cls.env.company.sale_confirmation_group_ids = cls.group_sale_admin
