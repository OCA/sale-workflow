/* Copyright 2025 Tecnativa - Carlos Roca
 * License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl). */
import {Component, t, useProps} from "@odoo/owl";
import {Dialog} from "@web/core/dialog/dialog";

export class ImageZoomDialog extends Component {
    static template = "sale_product_catalog_extended.ImageZoomDialog";
    static components = {Dialog};
    props = useProps({
        src: t.string(),
        title: t.string().optional(),
        close: t.function(),
    });
}
