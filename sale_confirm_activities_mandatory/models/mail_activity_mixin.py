# Copyright 2022 Camptocamp SA
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl)

from odoo import models


class MailActivityMixin(models.AbstractModel):
    _inherit = "mail.activity.mixin"

    def _check_validation_activities_todo(self):
        acts = self.activity_ids
        return not any(a.activity_category == "validation" for a in acts)
