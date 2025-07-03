<template>
  <div class="client-portal-container">
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

    <div class="card">
      <h2>Player Profiles</h2>
      <div v-if="playerProfiles.length > 1" class="profile-group">
        <div v-for="player in playerProfiles" :key="player.name" class="profile-avatar" @click="viewPlayer(player)">
          <img :src="player.profile_picture || '/assets/frappe/images/avatar.png'" :title="player.player_name" />
        </div>
      </div>
      <div v-else-if="playerProfiles.length === 1" class="profile-single">
         <div class="profile-overview" @click="viewPlayer(playerProfiles[0])">
            <img :src="playerProfiles[0].profile_picture || '/assets/frappe/images/avatar.png'" alt="Player Image" class="profile-avatar-large"/>
            <h4>{{ playerProfiles[0].player_name }}</h4>
        </div>
      </div>
       <p v-else>No player profiles found.</p>
    </div>

    <div class="card">
      <h2>Instrument Profiles</h2>
       <div v-if="instrumentProfiles.length > 1" class="profile-group">
        <div v-for="instrument in instrumentProfiles" :key="instrument.name" class="profile-avatar" @click="viewInstrument(instrument)">
          <img :src="instrument.instrument_image || '/assets/frappe/images/avatar.png'" :title="instrument.instrument_name" />
        </div>
      </div>
       <div v-else-if="instrumentProfiles.length === 1" class="profile-single">
         <div class="profile-overview" @click="viewInstrument(instrumentProfiles[0])">
            <img :src="instrumentProfiles[0].instrument_image || '/assets/frappe/images/avatar.png'" alt="Instrument Image" class="profile-avatar-large"/>
            <h4>{{ instrumentProfiles[0].instrument_name }}</h4>
            <p class="text-muted">{{instrumentProfiles[0].serial_number}}</p>
        </div>
      </div>
      <p v-else>No instrument profiles found.</p>
    </div>

  </div>
</template>

<script>
import { ref, onMounted } from 'vue';

export default {
  setup() {
    const clientInfo = ref({});
    const playerProfiles = ref([]);
    const instrumentProfiles = ref([]);

    onMounted(() => {
      // Get the client profile name from the URL, assuming it's passed as a parameter
      const clientProfileName = frappe.get_route()[1];
      if(clientProfileName){
        frappe.call({
          method: 'repair_portal.api.client_portal.get_client_portal_data',
          args: { client_profile_name: clientProfileName },
          callback: (r) => {
            if (r.message) {
              clientInfo.value = r.message.client_info;
              playerProfiles.value = r.message.player_profiles;
              instrumentProfiles.value = r.message.instrument_profiles;
            }
          },
        });
      }
    });

    const editClientInfo = () => {
      frappe.set_route('Form', 'Client Profile', clientInfo.value.name);
    };

    const viewPlayer = (player) => {
      if(player.route){
        frappe.set_route(player.route);
      } else {
        frappe.set_route('Form', 'Player Profile', player.name);
      }
    };

     const viewInstrument = (instrument) => {
      if(instrument.route){
        frappe.set_route(instrument.route);
      } else {
        frappe.set_route('Form', 'Instrument Profile', instrument.name);
      }
    };

    return {
      clientInfo,
      playerProfiles,
      instrumentProfiles,
      editClientInfo,
      viewPlayer,
      viewInstrument
    };
  },
};
</script>

<style scoped>
.client-portal-container {
  max-width: 900px;
  margin: 0 auto;
  padding: 20px;
}
.card {
  background: #fff;
  border-radius: 8px;
  padding: 20px;
  margin-bottom: 20px;
  box-shadow: 0 2px 4px rgba(0, 0, 0, 0.1);
}
.profile-header {
  display: flex;
  align-items: center;
}
.profile-picture img {
  width: 100px;
  height: 100px;
  border-radius: 50%;
  margin-right: 20px;
}
.profile-group {
    display: flex;
    flex-wrap: wrap;
}
.profile-avatar {
    cursor: pointer;
    margin: 5px;
    transition: transform 0.2s;
}
.profile-avatar:hover {
    transform: scale(1.1);
}
.profile-avatar img {
    width: 60px;
    height: 60px;
    border-radius: 50%;
    border: 2px solid #eee;
}
.profile-single {
    cursor: pointer;
}
.profile-overview {
    text-align: center;
}
.profile-avatar-large {
    width: 120px;
    height: 120px;
    border-radius: 50%;
    border: 3px solid #eee;
    margin-bottom: 10px;
}
</style>