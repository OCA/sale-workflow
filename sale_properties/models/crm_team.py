# Copyright 2024 KMEE
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).

from odoo import fields, models


class CrmOrder(models.Model):

    _inherit = "crm.team"

    sale_properties_definition = fields.PropertiesDefinition("Sale Properties")
