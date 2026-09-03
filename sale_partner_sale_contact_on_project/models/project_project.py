# Copyright 2026 OpenStudio SAS
# License LGPL-3.0 or later (https://www.gnu.org/licenses/lgpl).

from odoo import models


class ProjectProject(models.Model):
    _inherit = ["project.project", "sale.contact.mixin"]
    _name = "project.project"
