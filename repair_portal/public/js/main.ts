import { createApp } from 'vue';

const app = createApp({
  data() {
    return { message: 'Hello from Repair Portal!' };
  },
  template: '<div>{{ message }}</div>'
});

app.mount('#app');