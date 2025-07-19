<!-- File: client_portal/customer/Customer.vue -->
<!-- Last Updated: 2025-07-18 -->
<template>
  <section class="content">
    <div class="container-fluid">
      <div class="row">
        <div class="col-md-3">
          <div class="card card-primary card-outline">
            <div class="card-body box-profile text-center">
              <img class="profile-user-img img-fluid img-circle"
                   :src="client.avatar || '/assets/repair_portal/img/avatar5.png'"
                   alt="Client profile picture">
              <h3 class="profile-username mt-2">{{ client.full_name || 'Loading...' }}</h3>
              <p class="text-muted">{{ client.email }}</p>
            </div>
          </div>
        </div>

        <div class="col-md-9">
          <div class="card">
            <div class="card-header">
              <h5>Edit Profile</h5>
            </div>
            <div class="card-body">
              <form @submit.prevent="updateClient">
                <div class="form-group">
                  <label>Full Name</label>
                  <input v-model="client.full_name" class="form-control" required />
                </div>
                <div class="form-group">
                  <label>Email</label>
                  <input type="email" v-model="client.email" class="form-control" required />
                </div>
                <div class="form-group">
                  <label>Phone</label>
                  <input v-model="client.phone" class="form-control" />
                </div>
                <div class="form-group">
                  <label>Address</label>
                  <textarea v-model="client.address" class="form-control"></textarea>
                </div>
                <button type="submit" class="btn btn-primary">Save Changes</button>
              </form>
            </div>
          </div>
        </div>
      </div>
    </div>
  </section>
</template>

<script setup>
import { reactive, onMounted } from 'vue';

const client = reactive({});

onMounted(() => {
  const clientId = new URL(window.location.href).searchParams.get('client_id');
  if (!clientId) return;

  frappe.call({
    method: 'repair_portal.api.get_customer',
    args: { client_id: clientId },
    callback: r => {
      if (r.message && typeof r.message === 'object') {
        Object.assign(client, r.message);
      }
    }
  });
});

function updateClient() {
  frappe.call({
    method: 'repair_portal.api.update_customer',
    args: { client },
    callback: r => {
      if (r.message === 'success') {
        frappe.msgprint('Profile updated successfully');
      } else {
        frappe.msgprint({ title: 'Error', message: 'Failed to update profile', indicator: 'red' });
      }
    }
  });
}
</script>

<style scoped>
.profile-user-img {
  width: 100px;
  height: 100px;
  object-fit: cover;
}
.mt-2 {
  margin-top: 0.5rem;
}
</style>