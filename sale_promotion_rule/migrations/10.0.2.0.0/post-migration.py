# -*- coding: utf-8 -*-
# Copyright 2019 ACSONE SA/NV
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).


def migrate(cr, version):
    if not version:
        return
    # Set is_minimal_amount_tax_incl value
    cr.execute("""
        update sale_promotion_rule
        set is_minimal_amount_tax_incl=true
        where restriction_amount_field='amount_total';
        """)
    cr.execute("""
        update sale_promotion_rule
        set is_minimal_amount_tax_incl=false
        where restriction_amount_field='amount_untaxed';
        """)
