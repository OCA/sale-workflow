# coding: utf-8

import logging

_logger = logging.getLogger(__name__)


def migrate(cr, version):
    _logger.info(
        "Multiply by 100 Product Margin Classification Rates. (Markup field)")
    cr.execute("""
    UPDATE product_margin_classification
    SET markup = markup * 100
    """)
    _logger.info(
        "Product Template. Margin state: Replace 'cheap' by 'too_cheap'")
    cr.execute("""
    UPDATE product_template
    SET margin_state = 'too_cheap'
    WHERE margin_state = 'cheap'
    """)
    _logger.info(
        "Product Template. Margin state:"
        " Replace 'expensive' by 'too_expensive'")
    cr.execute("""
    UPDATE product_template
    SET margin_state = 'too_expensive'
    WHERE margin_state = 'expensive'
    """)
    _logger.info(
        "Product Template. Margin state: Replace 'ok' by 'correct'")
    cr.execute("""
    UPDATE product_template
    SET margin_state = 'correct'
    WHERE margin_state = 'ok'
    """)
