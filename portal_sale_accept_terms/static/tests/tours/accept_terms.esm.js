/** @odoo-module **/
import tour from "web_tour.tour";

tour.register(
    "portal_sale_accept_terms.accept_terms",
    {
        test: true,
    },
    [
        {
            content: "Click on Accept & Sign",
            trigger: "a:contains('Accept & Sign')",
            run: "click",
        },
        {
            content: "Check that submit button is disabled",
            trigger: "button.o_portal_sign_submit[disabled]",
            // eslint-disable-next-line no-empty-function
            run: () => {},
        },
        {
            content: "Accept the terms",
            trigger: "#portal_accept_terms",
            run: "click",
        },
        {
            content: "Check that submit button is enabled",
            trigger: "button.o_portal_sign_submit:not(:disabled)",
            // eslint-disable-next-line no-empty-function
            run: () => {},
        },
    ]
);
