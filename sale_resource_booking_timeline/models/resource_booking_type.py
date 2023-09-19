from odoo import api, fields, models


class ResourceBookingType(models.Model):
    _inherit = "resource.booking.type"

    duration_in_timeline = fields.Float(
        string="Duration in timeline",
        default=0.5,  # 30 minutes
    )

    @api.onchange("duration")
    def _onchange_duration(self):
        self.duration_in_timeline = self.duration
