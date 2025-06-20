frappe.pages['adhesive_timer'].on_page_load = function(wrapper) {
    let page = frappe.ui.make_app_page({
        parent: wrapper,
        title: 'Real-Time Adhesive Timer',
        single_column: true
    });

    page.set_primary_action('Start Timer', () => {
        let seconds = 0;
        const interval = setInterval(() => {
            seconds++;
            page.main.find('.adhesive-timer-display').html(`Elapsed Time: ${seconds} sec`);
        }, 1000);

        frappe.msgprint('Timer started. Click reload to stop.');
    });

    $(wrapper).html(`
        <div class="adhesive-timer-display" style="font-size: 24px; margin-top: 20px;">Elapsed Time: 0 sec</div>
    `);
};