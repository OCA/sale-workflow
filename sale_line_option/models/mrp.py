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


class MrpBomLine(models.Model):
    _inherit = "mrp.bom.line"
    _rec_name = 'name'

    name = fields.Char(compute='_compute_name', store=True, index=True)
    opt_max_qty = fields.Integer(
        string="Max Qty Opt", oldname='max_qty',
        help="High limit authorised in the sale line option",
        default=1)

    @api.multi
    @api.depends('product_id', 'product_id.product_tmpl_id.name')
    def _compute_name(self):
        for rec in self:
            rec.name = rec.product_id.name

    @api.model
    def name_search(self, name='', args=None, operator='ilike', limit=100):
        new_domain = self._filter_bom_lines_for_sale_line_option(args)
        res = super(MrpBomLine, self).name_search(
            name=name, args=new_domain, operator=operator, limit=limit)
        return res

    def search(self, domain, offset=0, limit=None, order=None, count=False):
        new_domain = self._filter_bom_lines_for_sale_line_option(domain)
        return super(MrpBomLine, self).search(
            new_domain, offset=offset, limit=limit, order=order, count=count)

    @api.model
    def _filter_bom_lines_for_sale_line_option(self, domain):
        product = self.env.context.get('filter_bom_with_product')
        if isinstance(product, int):
            product = self.env['product.product'].browse(product)
        if product:
            new_domain = [
                '|',
                '&',
                ('bom_id.product_tmpl_id', '=', product.product_tmpl_id.id),
                ('bom_id.product_id', '=', False),
                ('bom_id.product_id', '=', product.id)]
            domain += new_domain
        return domain
