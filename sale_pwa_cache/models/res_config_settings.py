# Copyright 2021 Tecnativa - Alexandre D. Díaz
# License LGPL-3.0 or later (https://www.gnu.org/licenses/lgpl).

from odoo import api, fields, models


class ResConfigSettings(models.TransientModel):
    _inherit = "res.config.settings"

    pwa_sale_auto_confirm = fields.Boolean(
        "PWA Sale Auto-Confirm",
        help="Enables auto-confirm when offline records are syncronized",
        default=True,
    )

    @api.model
    def get_values(self):
        config_parameter_obj_sudo = self.env["ir.config_parameter"].sudo()
        res = super(ResConfigSettings, self).get_values()
        res["pwa_sale_auto_confirm"] = config_parameter_obj_sudo.get_param(
            "pwa.sale.auto.confirm", default="True"
        )
        return res

    @api.model
    def set_values(self):
        config_parameter_obj_sudo = self.env["ir.config_parameter"].sudo()
        res = super(ResConfigSettings, self).set_values()
        config_parameter_obj_sudo.set_param(
            "pwa.sale.auto.confirm", self.pwa_sale_auto_confirm
        )
        return res
