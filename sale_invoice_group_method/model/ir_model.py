# Copyright 2017 Eficent Business and IT Consulting Services, S.L.
# License LGPL-3.0 or later (https://www.gnu.org/licenses/lgpl.html).

from odoo import api, models


class IrModelFields(models.Model):
    _inherit = 'ir.model.fields'

    @api.multi
    def name_get(self):
        res = []
        context = self._context
        if context.get('sale_invoice_group_method', True):
            for field in self:
                res.append((field.id, '%s' % field.field_description))
            return res
        return super(IrModelFields, self).name_get()
