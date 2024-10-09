# Copyright 2020 Tecnativa - Carlos Dauden
# Copyright 2020 Tecnativa - Sergio Teruel
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).

from odoo import fields, models


class ResUsers(models.Model):
    _inherit = "res.users"

    commercial_journal_ids = fields.Many2many(
        comodel_name="account.journal",
        string="Allowed journals for commercial",
    )
