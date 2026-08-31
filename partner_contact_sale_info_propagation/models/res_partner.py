# Copyright 2019 Tecnativa - Ernesto Tejeda
# Copyright 2021 Tecnativa - Víctor Martínez
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).
from odoo import models
from odoo.tools import config


class ResPartner(models.Model):
    _inherit = "res.partner"

    def _check_propagation_allowed(self):
        return bool(
            not config["test_enable"]
            or (config["test_enable"] and self.env.context.get("test_propagation"))
        )

    def write(self, vals):
        """Propagate the Salesperson change in the partner to the child contacts.

        Odoo only sets the salesperson of the parent on its contacts when they
        are created or re-parented and they have no salesperson yet (see
        `res.partner._compute_user_id`), so here we take care of the later
        changes done in the company, updating the contacts that have no
        salesperson or that still have the previous one of the company.
        """
        if "user_id" not in vals or not self._check_propagation_allowed():
            return super().write(vals)
        for record in self:
            childs = record.child_ids.filtered(
                lambda child, user=record.user_id: not child.user_id
                or child.user_id == user
            )
            if childs:
                # Recursive call that propagates down the whole hierarchy
                childs.write({"user_id": vals["user_id"]})
        return super().write(vals)
