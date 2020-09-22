# Copyright 2020 Ecosoft Co., Ltd. (http://ecosoft.co.th)
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).

from odoo import _, models


class QueueJob(models.Model):
    """ Job status and result """

    _inherit = "queue.job"

    def _related_action_sale_automatic_workflow(self):
        obj = self.args[0]
        action = {
            "name": _("Sale Automatic Workflow Job"),
            "type": "ir.actions.act_window",
            "res_model": obj._name,
            "view_mode": "form",
            "res_id": obj.id,
        }
        return action
