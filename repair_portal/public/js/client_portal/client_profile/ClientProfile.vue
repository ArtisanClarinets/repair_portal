<!-- File: client_portal/client_profile/ClientProfile.vue -->
<!-- Last Updated: 2025-07-16 -->
<template>
  <section class="content">
    <div class="container-fluid">
      <div class="row">
        <div class="col-md-3">
          <div class="card card-primary card-outline">
            <div class="card-body box-profile">
              <div class="text-center">
                <img class="profile-user-img img-fluid img-circle"
                     :src="client.avatar || '/assets/repair_portal/img/avatar5.png'"
                     alt="Client profile picture">
              </div>
              <h3 class="profile-username text-center">{{ client.full_name || 'Loading...' }}</h3>
              <p class="text-muted text-center">{{ client.email || '' }}</p>
            </div>
          </div>
        </div>

        <div class="col-md-9">
          <div class="card">
            <div class="card-header p-2">
              <h5>Repair Summary</h5>
            </div>
            <div class="card-body">
              <strong>Total Repairs:</strong> {{ client.total_repairs || 0 }}
            </div>
          </div>
        </div>
      </div>
    </div>
  </section>
</template>

<script>
export default {
  name: "ClientProfile",
  data() {
    return {
      client: {}
    };
  },
  mounted() {
    const clientId = new URLSearchParams(window.location.search).get('client_id');
    if (!clientId) return;

    frappe.call({
      method: 'repair_portal.api.get_client_profile',
      args: { client_id: clientId },
      callback: r => {
        if (r.message) {
          this.client = r.message;
        }
      }
    });
  }
};
</script>

<style scoped>
.profile-user-img {
  width: 100px;
  height: 100px;
  object-fit: cover;
}
</style>