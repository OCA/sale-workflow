# Copyright 2019 Alexandre Díaz
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo import api, fields, models


class ResPartner(models.Model):
    _inherit = "res.partner"

    type = fields.Selection(selection_add=[("ordering", "Ordering contact")])
    has_ordering_contact_child = fields.Boolean(
        compute="_compute_has_ordering_contact_child",
        help="Technical field for use in views",
        store=True,
    )

    @api.depends("child_ids.type")
    def _compute_has_ordering_contact_child(self):
        datas = self.read_group(
            [("parent_id", "in", self.ids), ("type", "=", "ordering")],
            ["parent_id"],
            groupby=["parent_id"],
        )
        parent_ids = {data["parent_id"][0] for data in datas}
        with_ordering_c_recs = self.browse(parent_ids)
        with_ordering_c_recs.update({"has_ordering_contact_child": True})
        without_ordering_c_recs = self - with_ordering_c_recs
        without_ordering_c_recs.update({"has_ordering_contact_child": False})
