# Copyright 2020 Camptocamp SA
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl)
from odoo import _, api, models

from .res_partner import WEEKDAY_MAPPING


class StockPicking(models.Model):
    _inherit = "stock.picking"

    @api.onchange('scheduled_date')
    def _onchange_scheduled_date(self):
        self.ensure_one()
        if (
            not self.partner_id or
            self.partner_id.delivery_schedule_preference != 'fix_weekdays' or
            self.picking_type_id.code != 'outgoing'
        ):
            return
        raw_scheduled_date_weekday = self.scheduled_date.weekday()
        scheduled_date_weekday = WEEKDAY_MAPPING.get(
            str(raw_scheduled_date_weekday)
        )
        p = self.partner_id
        if not p.is_preferred_delivery_weekday(scheduled_date_weekday):
            return {
                "warning": {
                    "title": _(
                        "Scheduled date does not match partner's Delivery "
                        "schedule preference."
                    ),
                    "message": _(
                        "The scheduled date is on a %s, but the partner is "
                        "set to prefer deliveries on following weekdays:\n%s"
                        % (
                            scheduled_date_weekday,
                            '\n'.join(
                                [
                                    "  * %s" % day
                                    for day
                                    in p.get_delivery_schedule_preferred_weekdays(
                                        translate=True
                                    )
                                ]
                            ),
                        )
                    ),
                }
            }
