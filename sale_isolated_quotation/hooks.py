# -*- coding: utf-8 -*-
# © 2017 Ecosoft (ecosoft.co.th).
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).


def post_init_hook(cr, registry):
    # Set is_order for old records
    cr.execute("""
        update sale_order
        set is_order = true
        where state not in ('draft', 'cancel')
    """)
