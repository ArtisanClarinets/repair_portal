// relative path: repair_portal/instrument_profile/public/js/client_profile_portal.js
// updated: 2025-06-15
// version: 1.0.0
// purpose: JavaScript enhancements for Client-Created Instrument Profiles (customer portal)

frappe.ready(function () {
    const tooltips = document.querySelectorAll('[data-tooltip]');
    tooltips.forEach(el => {
        el.addEventListener('mouseenter', () => {
            const tooltip = document.createElement('div');
            tooltip.classList.add('custom-tooltip');
            tooltip.innerText = el.dataset.tooltip;
            el.appendChild(tooltip);
        });
        el.addEventListener('mouseleave', () => {
            const tooltip = el.querySelector('.custom-tooltip');
            if (tooltip) tooltip.remove();
        });
    });

    const stepper = document.querySelectorAll('.step-counter');
    stepper.forEach((el, idx) => {
        el.innerText = `Step ${idx + 1}`;
    });
});