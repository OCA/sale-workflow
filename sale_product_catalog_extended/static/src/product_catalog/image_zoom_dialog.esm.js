/* Copyright 2025 Tecnativa - Carlos Roca
 * License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl). */
import {Component} from "@odoo/owl";
import {Dialog} from "@web/core/dialog/dialog";

export class ImageZoomDialog extends Component {
    static template = "sale_product_catalog_extended.ImageZoomDialog";
    static components = {Dialog};
    static props = {
        src: String,
        title: {type: String, optional: true},
        close: Function,
    };
}
