# Copyright 2020 Ecosoft Co., Ltd. (http://ecosoft.co.th)
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).

from ast import literal_eval

from odoo import _, models


class QueueJob(models.Model):
    """ Job status and result """

    _inherit = "queue.job"

    def _related_action_sale_automatic_workflow(self):
        self.ensure_one()
        result = literal_eval(str(self.result))
        if result:
            record_ids = result.get("ids", False)
            model_name = result.get("model", False)
            records = (
                record_ids
                and model_name
                and self.env[model_name].browse(record_ids).exists()
            )
            if records:
                action = {
                    "name": _("Related Record"),
                    "type": "ir.actions.act_window",
                    "view_mode": "form",
                    "res_model": records._name,
                }
                if len(records) == 1:
                    action["res_id"] = records.id
                else:
                    action.update(
                        {
                            "name": _("Related Records"),
                            "view_mode": "tree,form",
                            "domain": [("id", "in", records.ids)],
                        }
                    )
                return action
