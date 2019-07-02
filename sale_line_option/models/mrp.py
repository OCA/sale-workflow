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
    optionnal_bom_line_ids = fields.One2many(
        'mrp.bom.line', 'bom_id', 'BoM Lines', copy=False)


class MrpBomLine(models.Model):
    _inherit = "mrp.bom.line"
    _rec_name = 'name'

    name = fields.Char(compute='_compute_name', store=True, index=True)
    opt_min_qty = fields.Integer(
        string="Min Qty", default=0)
    opt_default_qty = fields.Integer(
        string="Default Qty", oldname='default_qty', default=0,
        help="This is the default quantity set to the sale line option ")
    opt_max_qty = fields.Integer(
        string="Max Qty", oldname='max_qty', default=1,
        help="High limit authorised in the sale line option")
    # optionnal_bom_line_ids is exactly the same as bom_line_ids
    # this field is only here to be able to have a better view when activating
    # the with option parameter.
    # copy is set to false as bom_line_ids is already set to true

    # _sql_constraints = [
    #     ('bom_opt_qty_min', 'CHECK (opt_min_qty<=opt_default_qty)',
    #         'Default qty could not be lower than min qty.\n'),
    #     ('bom_opt_qty_max', 'CHECK (opt_default_qty<=opt_max_qty)',
    #         'Default qty could not be greather than max qty.\n'),
    #     ('bom_opt_qty_min_max', 'CHECK (opt_min_qty<=opt_max_qty)',
    #         'Min qty could not be greather than min qty.\n'),
    # ]

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

    # TODO remove this hack
    # instead of passing a context we can just create a method that
    # call the search with the right domain
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
