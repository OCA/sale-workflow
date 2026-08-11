/* Copyright 2026 Moduon
 * License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl). */
import {registry} from "@web/core/registry";
import {stepUtils} from "@web_tour/tour_utils";

registry.category("web_tour.tours").add("sale_order_line_description_manual_edit", {
    steps: () => [
        {
            content: "Open the sale order line editor",
            trigger:
                '.o_field_product_label_section_and_note_cell:contains("Sale description for test product")',
            run: "click",
        },
        {
            content: "Edit the sale order line description",
            trigger:
                ".o_selected_row .o_field_product_label_section_and_note_cell textarea",
            run: "edit Sale description for test product test",
        },
        ...stepUtils.saveForm(),
    ],
});
