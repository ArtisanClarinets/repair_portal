/* ClarinetFest AJAX loader – v3.1.0 */
frappe.ready(() => {
  const shell = document.querySelector('.catalog-wrapper > div[aria-live]');
  if (!shell) return;

  const BUCKET_KEYS = window.clarinetfest_bucket_keys || [];

  function fetchAndRender(q = "") {
    frappe.call({
      method: "clarinetfest.api.get_catalog_items",
      args: { search: q },
      callback: ({ message }) => {
        if (!message) return;
        render(message.items || {});
      }
    });
  }

  function render(buckets) {
    shell.innerHTML = "";
    // always put the three main buckets first
    BUCKET_KEYS.forEach(key => drawBucket(key, buckets[key] || []));
    // then any extras
    Object.keys(buckets)
      .filter(k => !BUCKET_KEYS.includes(k))
      .forEach(k => drawBucket(k, buckets[k]));
  }

  function drawBucket(key, arr) {
    const title = key ? key.replace(/^\w/, c => c.toUpperCase()) : "Other";
    shell.insertAdjacentHTML("beforeend",
      `<h2>${frappe.utils.xss_sanitise(title)}</h2>` +
      (arr.length
        ? `<div class="item-grid">${arr.map(card).join("")}</div>`
        : `<p class="no-data">No ${title.toLowerCase()} available right now.</p>`) );
  }

  function card(itm) {
    return `<a href="${frappe.utils.xss_sanitise(itm.route)}?from=clarinetfest"
              class="item-card-link" aria-label="${frappe.utils.xss_sanitise(itm.item_name || itm.item_code)}">
              <div class="item-card" id="${slug(itm.item_code)}">
                ${itm.website_image ? `<img src="${itm.website_image}" loading="lazy">` : ""}
                <div class="item-name">${frappe.utils.xss_sanitise(itm.web_item_name || itm.item_name)}</div>
                <div class="item-desc">${frappe.utils.xss_sanitise(itm.short_description || "")}</div>
              </div>
            </a>`;
  }

  const slug = s => s.toLowerCase().replace(/[^a-z0-9]+/g,"-");

  /* optional: hook live-filter box so a hard page refresh
     with ?search=foo in the URL immediately filters results */
  const urlQ  = frappe.utils.get_query_params().search || "";
  document.getElementById('liveFilter').value = urlQ;
  fetchAndRender(urlQ);
});
