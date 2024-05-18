# Copyright 2017 ForgeFlow S.L.
# Copyright 2017 Serpent Consulting Services Pvt. Ltd.
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl.html).

from odoo import fields, models


class SaleOrderLine(models.Model):
    _inherit = "sale.order.line"

    def _prepare_procurement_group_vals(self):
        values = super(SaleOrderLine, self)._prepare_procurement_group_vals()
        com_datetime = self.commitment_date
        com_date = fields.Date.to_string(com_datetime)
        if com_datetime and self._get_procurement_group_key()[0] == 12:
            values["name"] = "/".join([values["name"], com_date])
        return values

    def _prepare_procurement_values(self, group_id=False):
        values = super(SaleOrderLine, self)._prepare_procurement_values(
            group_id=group_id
        )
        com_datetime = self.commitment_date
        com_date = fields.Date.to_string(com_datetime)
        if com_datetime:
            values["date_planned"] = com_date
        return values

    def _get_procurement_group_key(self):
        """Return a key with priority to be used to regroup lines in multiple
        procurement groups. The higher the priority number is the more
        preference the criteria has.
        """
        priority = 12
        key = super(SaleOrderLine, self)._get_procurement_group_key()
        # Check priority
        if key[0] >= priority:
            return key
        com_datetime = self.commitment_date
        com_date = fields.Date.to_string(com_datetime)
        if com_date:
            return priority, com_date
        return key
