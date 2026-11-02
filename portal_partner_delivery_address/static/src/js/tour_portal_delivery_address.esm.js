/* @odoo-module */
/**
 * Tour: Portal Delivery Address Management.
 *
 * Covers AC1 (list addresses), AC2 (create delivery address), AC4 (select
 * shipping address on a quotation).
 *
 * This tour is driven by Python's HttpCase.start_tour() and requires the
 * test to set up a portal user, a sale order in 'sent' state, and at least
 * one delivery address before running.
 */

import {registry} from "@web/core/registry";

registry.category("web_tour.tours").add("portal_delivery_address_tour", {
    url: "/my/addresses",
    test: true,
    steps: () => [
        // ------------------------------------------------------------------
        // AC1: Portal user can see their delivery addresses.
        // ------------------------------------------------------------------
        {
            trigger: ".o_portal_addresses",
            content: "Confirm /my/addresses page is loaded",
        },
        {
            trigger: "a.o_address_card_add_new[href*='address_type=delivery']",
            content: "Click 'Add a new delivery address' link",
            run: "click",
            expectUnloadPage: true,
        },
        // ------------------------------------------------------------------
        // AC2: Create a new delivery address.
        // ------------------------------------------------------------------
        {
            trigger: "input[name='name']",
            content: "Fill in the delivery address name",
            run: "edit Tour Delivery Address",
        },
        {
            trigger: "input[name='email']",
            content: "Fill in the email",
            run: "edit tour_addr@test.com",
        },
        {
            trigger: "input[name='phone']",
            content: "Fill in the phone",
            run: "edit +32498765432",
        },
        {
            trigger: "input[name='street']",
            content: "Fill in the street",
            run: "edit 123 Rue de la Loi",
        },
        {
            trigger: "input[name='city']",
            content: "Fill in the city",
            run: "edit Brussels",
        },
        {
            trigger: "input[name='zip']",
            content: "Fill in the zip code",
            run: "edit 1000",
        },
        {
            trigger: "button[id='save_address']",
            content: "Submit the new delivery address",
            run: "click",
            expectUnloadPage: true,
        },
        {
            trigger: ".o_portal_addresses",
            content: "Confirm redirect back to /my/addresses after save",
        },
        // ------------------------------------------------------------------
        // AC4: Select shipping address on a quotation.
        // ------------------------------------------------------------------
        {
            trigger: "a[href='/my/home']",
            content: "Navigate to portal home",
            run: "click",
            expectUnloadPage: true,
        },
        {
            trigger: "a[href*='/my/quotes']",
            content: "Navigate to quotations",
            run: "click",
            expectUnloadPage: true,
        },
        {
            trigger: "table a[href*='/my/orders/']",
            content: "Open the quotation",
            run: "click",
            expectUnloadPage: true,
        },
        {
            trigger: "#o_portal_change_shipping_btn",
            content: "Click the 'Change' shipping address link",
            run: "click",
        },
        {
            trigger: "#o_portal_shipping_modal.show",
            content: "Confirm the shipping address modal is open",
        },
        {
            trigger:
                "#o_portal_shipping_address_list input[type='radio']:not(:checked)",
            content: "Select a different shipping address",
            run: "click",
        },
        {
            trigger: "#o_portal_shipping_address_submit",
            content: "Submit the new shipping address",
            run: "click",
            expectUnloadPage: true,
        },
        {
            trigger: "#portal_shipping_address_section",
            content: "Confirm page reloaded with updated shipping address",
        },
    ],
});
