<template>
  <div class="client-profile-container">
    <div class="banner"></div>
    <div class="profile-header card">
      <div class="profile-picture">
        <img :src="clientInfo.profile_image || '/assets/frappe/images/avatar.png'" alt="Client Image" />
      </div>
      <div class="profile-info">
        <h1>{{ clientInfo.client_name }}</h1>
        <p>{{ clientInfo.email }}</p>
        <p>{{ clientInfo.phone }}</p>
        <button @click="editClientInfo" class="btn btn-primary btn-sm">Edit Profile</button>
      </div>
    </div>

    <div class="card-section">
      <div class="card">
        <h2>Player Profiles</h2>
        <div class="profile-grid">
          <div v-for="player in playerProfiles" :key="player.name" class="profile-card" @click="viewPlayer(player)">
            <img :src="player.profile_picture || '/assets/frappe/images/avatar.png'" />
            <h4>{{ player.player_name }}</h4>
          </div>
          <p v-if="!playerProfiles.length">No player profiles found.</p>
        </div>
      </div>

      <div class="card">
        <h2>Instrument Profiles</h2>
        <div class="profile-grid">
          <div v-for="instrument in instrumentProfiles" :key="instrument.name" class="profile-card" @click="viewInstrument(instrument)">
            <img :src="instrument.instrument_image || '/assets/frappe/images/avatar.png'" />
            <h4>{{ instrument.instrument_name }}</h4>
            <small>{{ instrument.serial_number }}</small>
          </div>
          <p v-if="!instrumentProfiles.length">No instrument profiles found.</p>
        </div>
      </div>

      <div class="card">
        <h2>Recent Service Records</h2>
        <ul>
          <li v-for="record in serviceRecords" :key="record.name">
            <strong>{{ record.service_type }}</strong> - {{ record.service_date }}
            <p>{{ record.notes }}</p>
          </li>
        </ul>
        <p v-if="!serviceRecords.length">No service records found.</p>
      </div>

      <div class="card">
        <h2>Documents</h2>
        <ul>
          <li v-for="doc in documents" :key="doc.url">
            <a :href="doc.url" target="_blank">{{ doc.title }}</a>
          </li>
        </ul>
        <p v-if="!documents.length">No documents found.</p>
      </div>
    </div>
  </div>
</template>

<script>
import { ref, onMounted } from "vue";

export default {
  setup() {
    const clientInfo = ref({});
    const playerProfiles = ref([]);
    const instrumentProfiles = ref([]);
    const serviceRecords = ref([]);
    const documents = ref([]);

    onMounted(() => {
      const clientProfileName = frappe.get_route()[1];
      if (clientProfileName) {
        frappe.call({
          method: "repair_portal.api.client_portal.get_client_portal_data",
          args: { client_profile_name: clientProfileName },
          callback: (r) => {
            if (r.message) {
              clientInfo.value = r.message.client_info;
              playerProfiles.value = r.message.player_profiles;
              instrumentProfiles.value = r.message.instrument_profiles;
              serviceRecords.value = r.message.service_records;
              documents.value = r.message.documents;
            }
          },
        });
      }
    });

    const editClientInfo = () => {
      frappe.set_route("Form", "Client Profile", clientInfo.value.name);
    };

    const viewPlayer = (player) => {
      frappe.set_route("Form", "Player Profile", player.name);
    };

    const viewInstrument = (instrument) => {
      frappe.set_route("Form", "Instrument Profile", instrument.name);
    };

    return {
      clientInfo,
      playerProfiles,
      instrumentProfiles,
      serviceRecords,
      documents,
      editClientInfo,
      viewPlayer,
      viewInstrument,
    };
  },
};
</script>

<style scoped>
.client-profile-container {
  max-width: 1100px;
  margin: 0 auto;
}
.banner {
  background: linear-gradient(to right, #4b6cb7, #182848);
  height: 150px;
}
.profile-header {
  display: flex;
  align-items: center;
  margin-top: -50px;
  padding: 20px;
  background: #fff;
  border-radius: 8px;
}
.profile-picture img {
  width: 120px;
  height: 120px;
  border-radius: 50%;
  border: 4px solid #fff;
  margin-right: 20px;
}
.profile-info h1 {
  margin: 0;
}
.card-section {
  margin-top: 20px;
}
.card {
  background: #fff;
  padding: 20px;
  margin-bottom: 20px;
  border-radius: 8px;
}
.profile-grid {
  display: flex;
  flex-wrap: wrap;
  gap: 10px;
}
.profile-card {
  width: 120px;
  text-align: center;
  cursor: pointer;
}
.profile-card img {
  width: 80px;
  height: 80px;
  border-radius: 50%;
}
</style>
