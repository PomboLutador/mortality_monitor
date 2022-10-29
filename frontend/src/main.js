import Vue from 'vue';
import VueRouter from 'vue-router';
import App from './App.vue';
import vuetify from './plugins/vuetify';
import 'roboto-fontface/css/roboto/roboto-fontface.css';
import '@mdi/font/css/materialdesignicons.css';
import mortality_monitor from "./components/mortality_monitor.vue";
Vue.config.productionTip = false;

const routes = [
  { path: '/', component: mortality_monitor },

]

const router = new VueRouter({

  mode: 'history',
  routes // short for `routes: routes`
})

Vue.use(VueRouter);
new Vue({
  router,
  vuetify,
  render: (h) => {
    return h(App);
  },
}).$mount('#app');
