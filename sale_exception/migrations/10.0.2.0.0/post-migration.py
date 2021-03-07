# -*- coding: utf-8 -*-
# (c) 2021 Hunki Enterprises BV
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl.html).

import ast
import logging
try:
    import astunparse
except ImportError:
    astunparse = False


class RewriteNames(ast.NodeTransformer):
    def visit_Name(self, node):
        if node.id == 'order' or node.id == 'line':
            return ast.copy_location(ast.Name(id='object', ctx=node.ctx), node)
        else:
            return node


def migrate(cr, version=None):
    """ Rename variables `order` and `line` in exception expressions as those
    names are not available any more in v10 onwards """

    if not astunparse:
        logging.getLogger(__name__).warning(
            'Python lib astunparse is not installed, using sloppy version of '
            'code rewriting. '
            'If your exceptions break, install it and rerun the migration.'
        )
        cr.execute(
            """update exception_rule set
            code=regexp_replace(code, ' (line|order)\\.', ' object.', 'g')
            where model in ('sale.order', 'sale.order.line')"""
        )
        return
    cr.execute(
        'select id, code from exception_rule where model in %s',
        (('sale.order', 'sale.order.line'),),
    )
    for exception_id, code in cr.fetchall():
        new_code = astunparse.unparse(RewriteNames().visit(ast.parse(code)))
        cr.execute(
            'update exception_rule set code=%s where id=%s',
            (new_code, exception_id),
        )
