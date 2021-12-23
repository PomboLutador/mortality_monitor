<template>
  <v-app>
    <v-app-bar
      app
      color="indigo darken-1"
      dark
    >
      <h2>
      Mortality Monitor
      </h2>
      <v-spacer></v-spacer>
      <v-btn
        href="https://appsso.eurostat.ec.europa.eu/nui/show.do?dataset=demo_r_mweek3&lang=en"
        target="_blank"
        text
      >
        <span>Data source</span>
        <v-icon>mdi-open-in-new</v-icon>
      </v-btn>
      <v-btn
        href="https://github.com/PomboLutador/mortality_monitor"
        target="_blank"
        text
      >
        <span>Source code (GitHub)</span>
        <v-icon>mdi-open-in-new</v-icon>
      </v-btn>
    </v-app-bar>
    <v-main>
      <Homepage/>
    </v-main>
  </v-app>
</template>

<script>
import Homepage from './components/Homepage.vue';

export default {
  name: 'App',
  components: {
    Homepage,
  },
};
</script>
