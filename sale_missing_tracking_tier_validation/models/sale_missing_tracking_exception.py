# Copyright 2021 Tecnativa - Carlos Dauden
# Copyright 2021 Tecnativa - Sergio Teruel
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).

from odoo import models


class SaleMissingTrackingException(models.Model):
    _inherit = ["sale.missing.tracking.exception", "tier.validation"]
    _name = "sale.missing.tracking.exception"
    _state_from = ["request"]
    _state_to = ["approved"]

    def action_request(self):
        self.request_validation()
