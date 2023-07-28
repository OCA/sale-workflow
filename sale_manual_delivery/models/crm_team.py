# Copyright 2017 Denis Leemann, Camptocamp SA
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

from odoo import fields, models


class CrmTeam(models.Model):
    _inherit = "crm.team"

    manual_delivery = fields.Boolean(
        help="If enabled, the deliveries are not created at SO confirmation. "
        "You need to use the Create Delivery button in order to reserve and "
        "ship the goods.",
        default=False,
    )
