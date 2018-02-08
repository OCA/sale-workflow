# coding: utf-8
# Copyright (C) 2018 - Today: GRAP (http://www.grap.coop)
# @author: Sylvain LE GAL (https://twitter.com/legalsylvain)
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

__name__ = u"Precompute 'markup' field, based on the obsolete 'margin' field"


def compute_markup(cr):
    sql = """
    UPDATE product_margin_classification
    SET margin = margin / 100"""
    cr.execute(sql)


def migrate(cr, version):
    if not version:
        return
    compute_markup(cr)
