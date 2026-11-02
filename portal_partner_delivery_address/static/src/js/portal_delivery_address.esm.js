/* @odoo-module */
/**
 * Portal Delivery Address – frontend JS.
 *
 * Handles AJAX form submission for the shipping address modal so the page
 * does not do a full reload (progressive enhancement – the form still works
 * without JS via the standard POST action).
 */

function initShippingAddressModal() {
    const form = document.getElementById("o_portal_shipping_address_form");
    if (!form) {
        return;
    }

    const radioInputs = form.querySelectorAll(
        'input[type="radio"][name="shipping_partner_id"]'
    );
    radioInputs.forEach((radio) => {
        radio.addEventListener("change", () => {
            form.querySelectorAll(".list-group-item").forEach((item) => {
                item.classList.remove("active");
            });
            const activeLabel = radio.closest(".list-group-item");
            if (activeLabel) {
                activeLabel.classList.add("active");
            }
        });
    });

    form.addEventListener("submit", async (ev) => {
        ev.preventDefault();
        const formData = new FormData(form);
        const shippingPartnerId = formData.get("shipping_partner_id");

        if (!shippingPartnerId) {
            return;
        }
        const url = form.getAttribute("action");
        try {
            const response = await fetch(url, {
                method: "POST",
                body: formData,
                headers: {Accept: "application/json"},
            });
            const data = await response.json();
            if (data.success && data.redirect) {
                window.location.href = data.redirect;
            } else if (data.error) {
                console.error("Shipping address update error:", data.error);
            }
        } catch {
            // Network error – fall back to native form POST.
            form.submit();
        }
    });
}

document.addEventListener("DOMContentLoaded", initShippingAddressModal);
