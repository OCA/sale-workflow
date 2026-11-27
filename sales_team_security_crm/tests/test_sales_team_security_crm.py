# Copyright 2021 Tecnativa - Víctor Martínez
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo.addons.sales_team_security.tests.common import TestCommon


class TestSalesTeamSecurityCrm(TestCommon):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.record = cls.env["crm.lead"].create(
            {
                "name": "Test lead",
                "partner_id": cls.partner.id,
                "user_id": cls.user.id,
                "team_id": cls.team.id,
            }
        )

    def test_crm_lead_permissions(self):
        self._check_whole_permission_set(extra_checks=False)
