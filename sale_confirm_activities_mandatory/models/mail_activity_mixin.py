# Copyright 2022 Camptocamp SA
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl)

from odoo import models


class MailActivityMixin(models.AbstractModel):
    _inherit = "mail.activity.mixin"

    def _check_validation_activities_todo(self):
        for rec in self:
            remaining_activities = rec.activity_ids.filtered(
                lambda a: a.activity_category == "validation"
            )

            if remaining_activities:
                return False
        return True
