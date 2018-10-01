# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

{
    "name": "Sale Forecast",
    "summary": "Sale forecast, based on procurement_sale_forecast",
    "version": "11.0.1.0.0",
    "author": "Domatix",
    "license": "AGPL-3",
    "category": "Sales",
    "website": "http://www.domatix.com",
    "contributors": [
        "Oihane Crucelaegui <oihanecrucelaegi@avanzosc.es>",
        "Ainara Galdona <ainaragaldona@avanzosc.es>",
        "Pedro M. Baeza <pedro.baeza@serviciosbaeza.com>",
        "Ana Juaristi <anajuaristi@avanzosc.es>",
        "Daniel Campos <danielcampos@avanzosc.es>",
    ],
    "depends": [
        "base",
        "product",
        "sale",
        "stock",
        "sale_stock",
    ],
    "data": ["security/ir.model.access.csv",
             "wizard/sale_forecast_load_view.xml",
             "views/sale_view.xml",
             ],
    "installable": True,
}
