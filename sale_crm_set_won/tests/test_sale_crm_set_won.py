# Copyright 2021 Pingo Tecnologia
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo.tests import common


class TestSaleCrmSetWon(common.SavepointCase):
    """ Test Sale CRM Set Won"""

    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.sale_order = cls.env["sale.order"].with_context(tracking_disable=True)
        cls.crm_lead = cls.env["crm.lead"].with_context(tracking_disable=True)
        cls.crm_stage = cls.env["crm.stage"]

    def test_set_won_1(self):
        crm_stage_new = self.env.ref("crm.stage_lead1")
        crm_stage_won = self.env.ref("crm.stage_lead4")

        self.env["ir.config_parameter"].sudo().set_param("crm_set_won", True)
        self.env["ir.config_parameter"].sudo().set_param(
            "crm_set_won_option", "choose_stage"
        )
        self.env["ir.config_parameter"].sudo().set_param("stage_id", crm_stage_won)

        crm_lead = self.crm_lead.create(
            {
                "name": "Test Opportunity",
                "stage_id": crm_stage_new,
                "partner_id": self.ref("base.res_partner_1"),
                "type": "opportunity",
            }
        )

        sale_order = self.env.ref("sale.sale_order_6")
        sale_order.write({"opportunity_id": crm_lead.id})
        sale_order.write({"state": "sale"})

        self.assertEqual(crm_lead.stage_id.id, crm_stage_won)

    def test_set_won_2(self):
        crm_stage_new = self.env.ref("crm.stage_lead1")
        crm_stage_won = self.env.ref("crm.stage_lead4")

        self.env["ir.config_parameter"].sudo().set_param("crm_set_won", True)
        self.env["ir.config_parameter"].sudo().set_param(
            "crm_set_won_option", "set_100"
        )

        crm_lead = self.crm_lead.create(
            {
                "name": "Test Opportunity",
                "stage_id": crm_stage_new,
                "partner_id": self.ref("base.res_partner_1"),
                "type": "opportunity",
            }
        )

        sale_order = self.env.ref("sale.sale_order_6")
        sale_order.write({"opportunity_id": crm_lead.id})
        sale_order.write({"state": "sale"})

        self.assertEqual(crm_lead.stage_id.id, crm_stage_won)
