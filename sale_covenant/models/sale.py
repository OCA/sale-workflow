# coding: utf-8
# © 2017 David BEAL @ Akretion
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

from odoo import api, fields, models


class SaleOrder(models.Model):
    _inherit = "sale.order"

    covenant_id = fields.Many2one(
        comodel_name='sale.covenant', string='Covenant',
        help="Covenant drive commitments on markets")

    @api.multi
    @api.onchange('partner_id')
    def onchange_partner_id(self):
        """ Update 'Covenant' fields when the partner is changed:
        """
        res = super(SaleOrder, self).onchange_partner_id()
        if not self.partner_id:
            self.covenant_id = False,
        else:
            self.covenant_id = self.partner_id.covenant_id.id
        return res

    @api.model
    def fields_view_get(self, view_id=None, view_type='form',
                        toolbar=False, submenu=False):
        """ View is modified allowing to covenant_id value
        """
        res = super(SaleOrder, self).fields_view_get(
            view_id=view_id, view_type=view_type, toolbar=toolbar,
            submenu=submenu)
        return (self.env['record.setting.rule']
                ._customize_view_according_to_setting_rule(
                    res, view_type, self))

    @api.multi
    def onchange(self, values, field_name, field_onchange):
        res = super(SaleOrder, self).onchange(
            values, field_name, field_onchange)
        res = self.env['record.setting.rule']._update_onchange_values(
            self._name, values, res, field_name)
        return res
