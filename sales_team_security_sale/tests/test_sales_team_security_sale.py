# Copyright 2021 Tecnativa - Víctor Martínez
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo.addons.sales_team_security.tests.common import TestCommon


class TestSalesTeamSecuritySale(TestCommon):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        # Remove this variable in v16 and put instead:
        # from odoo.addons.base.tests.common import DISABLED_MAIL_CONTEXT
        DISABLED_MAIL_CONTEXT = {
            "tracking_disable": True,
            "mail_create_nolog": True,
            "mail_create_nosubscribe": True,
            "mail_notrack": True,
            "no_reset_password": True,
        }
        cls.env = cls.env(context=dict(cls.env.context, **DISABLED_MAIL_CONTEXT))
        cls.record = cls.env["sale.order"].create(
            {
                "partner_id": cls.partner.id,
                "user_id": cls.user.id,
                "team_id": cls.team.id,
            }
        )

    def test_sale_order_permissions(self):
        self._check_whole_permission_set(extra_checks=False)
