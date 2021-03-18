# Copyright 2021 Pingo Tecnologia
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo import fields, models


class ResConfigSettings(models.TransientModel):

    _inherit = 'res.config.settings'

    crm_set_won = fields.Boolean(
        string="Set Opportunity as Won",
    )

    crm_set_won_option = fields.Selection(
        selection=[
            ('set_100','Set Probability as 100%'),
            ('choose_stage','Choose Stage'),
        ],
        string="What To Do?",
        required="[('crm_set_won','=',True)]",
        config_parameter='sale_crm_set_won.crm_set_won_option',
    )

    stage_id = fields.Many2one(
        comodel_name="crm.stage",
        string="Stage",
        config_parameter='sale_crm_set_won.stage_id',
    )