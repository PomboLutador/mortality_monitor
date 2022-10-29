<template>
  <v-app>
    <v-app-bar app color="indigo darken-1" dark>
      <v-col cols="3">
        <v-row class="text-left">
          <v-col cols="3"> </v-col>
          <v-col cols="2"> </v-col>
        </v-row>
      </v-col>
      <v-col cols="5"></v-col>
      <v-col cols="4">
        <v-row class="text-right">
          <v-col cols="3"> </v-col>
          <v-col cols="3"></v-col>
          <v-col cols="5">
            <v-btn
              href="https://github.com/PomboLutador/mortality_monitor"
              target="_blank"
              text
            >
              GitHub (PomboLutador)
              <v-icon>mdi-open-in-new</v-icon>
            </v-btn></v-col
          >
          <v-col cols="1"> </v-col>
        </v-row>
      </v-col>
    </v-app-bar>
    <v-navigation-drawer
      color="indigo darken-1 bx-5"
      permanent
      floating
      app
      dark
    >
      <div v-if="currentRoute == '/'">
        <h2 class="text-left px-5 mt-4 white--text">Introduction</h2>
        <p class="text-left px-5 white--text">
          This website allows tracking of all-cause mortality in various age
          groups on a weekly basis for a variety of European countries.
        </p>
        <h2 class="px-5 white--text">Methodology</h2>
        <p class="text-left px-5 white--text">
          Weekly mortality data is pulled from EUROSTAT's
          <i>demo_r_mweek3</i> table. To compute expected deaths for a given
          weekly period <b>p</b>, the average of the 3 previous datapoints with
          the same calendar week is computed. Datapoints not within mean +-
          standard deviation are disregarded.
          <br />
          <br />
          A linear regression is fit through the prior 3 years of yearly deaths,
          starting from <b>p - 104 weeks</b> to <b>p - 52 weeks</b>. The growth
          of that linear regression is applied to the above calculated mean of
          previous observations to arrive at the expectation value for <b>p</b>.
          The moving average over 4 weeks is computed to smooth out the
          resulting expected deaths time series.
        </p>

        <v-btn
          href="https://appsso.eurostat.ec.europa.eu/nui/show.do?dataset=demo_r_mweek3&lang=en"
          target="_blank"
          text
        >
          Eurostat
          <v-icon>mdi-open-in-new</v-icon>
        </v-btn>
        <v-btn
          href="https://github.com/PomboLutador/mortality_monitor"
          target="_blank"
          text
        >
          Source code
          <v-icon>mdi-open-in-new</v-icon>
        </v-btn>
      </div>
    </v-navigation-drawer>
    <v-main>
      <router-view></router-view>
    </v-main>
  </v-app>
</template>


<script>
export default {
  name: "App",
  components: {},
  computed: {
    currentRoute() {
      return this.$route.path;
    },
  },
};
</script>
