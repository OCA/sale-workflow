# Copyright 2019 Open Source Integrators
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).

from odoo import models


class SaleOrder(models.Model):
    _name = "sale.order"
    _inherit = ["sale.order", "tier.validation"]
    _state_from = ["draft", "sent", "to approve"]
    _state_to = ["sale", "approved"]
