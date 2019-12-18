# Copyright 2017 Eficent Business and IT Consulting Services, S.L.
# License LGPL-3.0 or later (https://www.gnu.org/licenses/lgpl.html).

from odoo import api, models


class IrModelFields(models.Model):
    _inherit = 'ir.model.fields'

    def name_get(self):
        res = super().name_get()
        if self.env.context.get('sale_invoice_group_method'):
            res = dict(res)
            for field in self:
                res[field.id] = field.field_description
            res = list(res.items())
        return res
