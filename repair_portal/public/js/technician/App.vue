<script setup lang="ts">
import { onMounted, ref } from "vue";
import { createResource } from "frappe-ui";
import { Card } from "frappe-ui";

// Tiny helper to fetch counts
function useCount(doctype: string) {
  const count = ref<number | null>(null);
  async function load() {
    const res = await createResource({
      url: "/api/method/frappe.client.get_list",
      makeParams: () => ({
        doctype,
        fields: ["name"],
        limit_page_length: 0  // no paging, just count
      })
    }).fetch2(); // returns { message: [...] }
    count.value = Array.isArray(res.message) ? res.message.length : 0;
  }
  return { count, load };
}

const clients = useCount("Client Profile");
const instruments = useCount("Instrument Profile");
const players = useCount("Player Profile");

onMounted(async () => {
  await Promise.all([clients.load(), instruments.load(), players.load()]);
});
</script>

<template>
  <div class="p-6 space-y-6">
    <h2 class="text-2xl font-semibold">Technician Dashboard</h2>

    <div class="grid grid-cols-3 gap-4">
      <Card>
        <template #header>Clients</template>
        <div class="text-4xl text-center">
          {{ clients.count ?? "…" }}
        </div>
      </Card>

      <Card>
        <template #header>Instruments</template>
        <div class="text-4xl text-center">
          {{ instruments.count ?? "…" }}
        </div>
      </Card>

      <Card>
        <template #header>Players</template>
        <div class="text-4xl text-center">
          {{ players.count ?? "…" }}
        </div>
      </Card>
    </div>
  </div>
</template>

<style scoped>
/* Add any technician-page–specific overrides here */
</style>
