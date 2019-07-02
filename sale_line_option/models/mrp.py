# coding: utf-8
# © 2015 Akretion, Valentin CHEMIERE <valentin.chemiere@akretion.com>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

from odoo import fields, api, models


class MrpProduction(models.Model):
    _inherit = 'mrp.production'

    def _generate_raw_moves(self, exploded_lines):
        options = {opt.product_id: opt.qty for opt in self.lot_id.option_ids}
        moves = super(MrpProduction, self.with_context(
            {'lot_options': options}))._generate_raw_moves(exploded_lines)
        if options:
            for move in moves:
                move.write({'product_uom_qty': options[move.product_id]})
        return moves

    def _generate_raw_move(self, bom_line, line_data):
        options = self.env.context.get('lot_options')
        if options and bom_line.product_id not in options:
            return self.env['stock.move']
        return super(MrpProduction, self)._generate_raw_move(
            bom_line, line_data)


class MrpBom(models.Model):
    _inherit = 'mrp.bom'

    with_option = fields.Boolean()
    # optionnal_bom_line_ids is exactly the same as bom_line_ids
    # this field is only here to be able to have a better view when activating
    # the with option parameter.
    # copy is set to false as bom_line_ids is already set to true
    optionnal_bom_line_ids = fields.One2many(
        'mrp.bom.line', 'bom_id', 'BoM Lines', copy=False)


class MrpBomLine(models.Model):
    _inherit = "mrp.bom.line"

    opt_min_qty = fields.Integer(
        string="Min Qty", default=0)
    opt_default_qty = fields.Integer(
        string="Default Qty", oldname='default_qty', default=0,
        help="This is the default quantity set to the sale line option ")
    opt_max_qty = fields.Integer(
        string="Max Qty", oldname='max_qty', default=1,
        help="High limit authorised in the sale line option")

    _sql_constraints = [
        ('bom_opt_qty_min', 'CHECK (opt_min_qty<=opt_default_qty)',
            'Default qty could not be lower than min qty.\n'),
        ('bom_opt_qty_max', 'CHECK (opt_default_qty<=opt_max_qty)',
            'Default qty could not be greather than max qty.\n'),
    ]
