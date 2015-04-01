# -*- coding: utf-8 -*-

from . import model


def populate_unrevisioned_name(cr, registry):
    cr.execute('UPDATE sale_order '
               'SET unrevisioned_name = name '
               'WHERE unrevisioned_name is NULL')
