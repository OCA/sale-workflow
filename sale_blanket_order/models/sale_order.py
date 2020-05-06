# Copyright 2018 ACSONE SA/NV
# Copyright 2019 Eficent and IT Consulting Services, S.L.
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).
from odoo import api, fields, models, _
from odoo.exceptions import ValidationError


class SaleOrder(models.Model):
    _inherit = 'sale.order'

    blanket_order_id = fields.Many2one(
        'sale.blanket.order', string='Origin blanket order',
        related='order_line.blanket_order_line.order_id')

    @api.model
    def _check_exchausted_blanket_order_line(self):
        return any(line.blanket_order_line.remaining_qty < 0.0 for
                   line in self.order_line)

    @api.multi
    def button_confirm(self):
        res = super().button_confirm()
        for order in self:
            if order._check_exchausted_blanket_order_line():
                raise ValidationError(_(
                    "Cannot confirm order %s as one of the lines refers to a"
                    " blanket order that has no remaining quantity.")
                    % order.name)
        return res

    @api.constrains('partner_id')
    def check_partner_id(self):
        for line in self.order_line:
            if line.blanket_order_line:
                if line.blanket_order_line.partner_id != \
                        self.partner_id:
                    raise ValidationError(_(
                        'The customer must be equal to the '
                        'blanket order lines customer'))
