# Copyright 2021 Pingo Tecnologia
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo import models


class SaleOrder(models.Model):

    _inherit = "sale.order"

    def write(self, values):
        state = values["state"] if "state" in values else False

        crm_set_won_option = (
            self.env["ir.config_parameter"]
            .sudo()
            .get_param("sale_crm_set_won.crm_set_won_option")
        )

        stage_id = (
            self.env["ir.config_parameter"]
            .sudo()
            .get_param("sale_crm_set_won.stage_id")
        )

        if crm_set_won_option and state in ["done", "sale"]:
            if self.opportunity_id:
                if crm_set_won_option == "set_100":
                    self.opportunity_id.probability = 100
                elif crm_set_won_option == "choose_stage":
                    self.opportunity_id.stage_id = int(stage_id)

        return super(SaleOrder, self).write(values)
