<template>
  <v-container>
    <v-row class="text-center mt-2">
      <v-col cols="1"> </v-col>
      <v-col cols="3">
        <v-select
          v-model="country_selection"
          :items="geo_options"
          item-value="name"
          item-text="name"
          label="Region"
          outlined
        ></v-select>
      </v-col>
      <v-col cols="4">
        <v-container fluid>
          <v-select
            v-model="age_groups_selection"
            :items="available_age_groups"
            label="Age groups"
            item-text="name"
            item-value="value"
            multiple
          ></v-select>
        </v-container>
      </v-col>
      <v-col cols="2">
        <v-select
          v-model="year_selection"
          :items="available_years"
          label="Starting year"
          outlined
        ></v-select>
      </v-col>
      <v-col cols="1">
        <v-select
          v-model="calendar_week_selection"
          :items="calendar_week_options"
          label="Calendar week"
          outlined
        ></v-select>
      </v-col>
      <v-col cols="1"> </v-col>
    </v-row>
    <v-row
      ><v-col cols="5"></v-col>
      <v-col cols="2">
        <center>
          <v-btn
            @click="
              get_excess_deaths_data(
                country_selection,
                age_groups_selection,
                year_selection
              );
              get_yearly_deaths_data(
                country_selection,
                age_groups_selection,
                year_selection,
                calendar_week_selection
              );
            "
            depressed
            elevation="2"
            class="font-weight-bold"
            v-on="on"
            >Draw!
          </v-btn>
          <v-tooltip bottom>
            <template v-slot:activator="{ on, attrs }">
              <v-icon color="primary" dark v-bind="attrs" v-on="on">
                mdi-information
              </v-icon> </template
            >If the selectors do not contain any values, please wait a second or
            try and refresh the page!
          </v-tooltip>
        </center>
      </v-col>
      <v-col cols="5"></v-col>
    </v-row>
    <v-row>
      <v-col class="mb-4" cols="12">
        <h1
          v-if="
            available_geos_query_is_successful == null &&
            available_ages_query_is_successful == null &&
            available_years_query_is_successful == null
          "
          class="text-center"
        >
          Please be patient while the data is being fetched
        </h1>
        <v-overlay
          v-if="
            available_geos_query_is_successful == null &&
            available_ages_query_is_successful == null &&
            available_years_query_is_successful == null
          "
        ></v-overlay>
        <v-progress-linear
          indeterminate
          color="primary"
          v-if="
            available_geos_query_is_successful == null &&
            available_ages_query_is_successful == null &&
            available_years_query_is_successful == null
          "
        ></v-progress-linear>
        <h5
          v-if="
            available_geos_query_is_successful == null &&
            available_ages_query_is_successful == null &&
            available_years_query_is_successful == null
          "
          class="text-center"
        >
          If you're the first viewer of the day, this might take a minute or
          two!
        </h5>
        <h2
          v-if="excess_deaths_request_successful"
          class="font-weight-bold mb-3 text-center"
        >
          Weekly all-cause mortality for country {{ country_selection }}
        </h2>
        <excess_deaths_chart
          v-if="excess_deaths_request_successful"
          :chartData="datacollection_excess_deaths_chart"
          class="mt-3"
        ></excess_deaths_chart>
      </v-col>
    </v-row>
    <v-row class="text-left">
      <v-col cols="12">
        <h2
          v-if="yearly_deaths_request_successful"
          class="text-center font-weight-bold mb-3"
        >
          Aggregated yearly deaths for country
          {{ country_selection }} until calendar week
          {{ calendar_week_selection }}
        </h2>
        <h6
          v-if="yearly_deaths_request_successful"
          class="text-center font-weight-bold mb-3"
        >
          <i
            >(If current year hasn't passed calendar week
            {{ calendar_week_selection }} yet, all available data for that year
            is considered.)</i
          >
        </h6>
        <yearly_deaths_chart
          v-if="yearly_deaths_request_successful"
          :chartData="datacollection_yearly_deaths_chart"
        ></yearly_deaths_chart>
      </v-col>
    </v-row>
  </v-container>
</template>

<script>
import axios from "axios";
import excess_deaths_chart from "./excess_deaths_chart.vue";
import yearly_deaths_chart from "./yearly_deaths_chart.vue";

export default {
  name: "mortality_monitor",

  data: () => ({
    // Query flags
    excess_deaths_request_successful: null,
    yearly_deaths_request_successful: null,
    available_geos_query_is_successful: null,
    available_ages_query_is_successful: null,
    available_years_query_is_successful: null,

    // UI selections
    calendar_week_selection: 53,
    year_selection: 2018,
    country_selection: "Switzerland",
    age_groups_selection: [
      "Y65-69",
      "Y70-74",
      "Y75-79",
      "Y80-84",
      "Y85-89",
      "Y_GE90",
    ],

    // UI options
    calendar_week_options: Array.from({ length: 53 }, (x, i) => i + 1),
    geo_options: [],
    available_age_groups: [],
    available_years: [],

    // Chart data
    labels: [],
    datacollection_excess_deaths_chart: {},
    datacollection_yearly_deaths_chart: {},
  }),

  components: {
    excess_deaths_chart,
    yearly_deaths_chart,
  },

  mounted() {
    // Get available geos
    const available_geos_url = "<placeholder>/available_geos";
    axios
      .get(available_geos_url, {})
      .then((res) => {
        this.geo_options = res.data.sort();
        this.available_geos_query_is_successful = true;
      })
      .catch((error) => {
        console.error(error);
      });

    // Get available age groups
    const available_ages_url = "<placeholder>/available_ages";
    axios
      .get(available_ages_url, {})
      .then((res) => {
        this.available_age_groups = Object.entries(res.data).map((arr) => ({
          name: arr[1],
          value: arr[0],
        }));
        this.available_ages_query_is_successful = true;
      })
      .catch((error) => {
        console.error(error);
      });

    // Get available years
    const available_years_url = "<placeholder>/available_years";
    axios
      .get(available_years_url, {})
      .then((res) => {
        this.available_years = res.data;
        this.available_years_query_is_successful = true;
      })
      .catch((error) => {
        console.error(error);
      });
  },
  methods: {
    get_excess_deaths_data(geo_choice, age_choices, year_choice) {
      const backend_url = "<placeholder>/excess_deaths";
      axios
        .post(backend_url, {
          "Geopolitical entity (reporting)": geo_choice,
          "Age class": age_choices,
          year: year_choice,
        })
        .then((res) => {
          this.labels = res.data.label;
          this.deaths = res.data.deaths;
          this.expected_deaths = res.data.expected_deaths;
          this.above_expectation_deaths = res.data.above_expectation_deaths;
          this.below_expectation_deaths = res.data.below_expectation_deaths;
          this.datacollection_excess_deaths_chart = {
            labels: this.labels,
            datasets: [
              {
                pointBackgroundColor: "#000000",
                pointBorderColor: "#000000",
                borderWidth: 2,
                pointRadius: 1,
                type: "line",
                backgroundColor: "#000000",
                borderColor: "#000000",
                label: "Expected deaths",
                data: this.expected_deaths,
                fill: false,
                lineTension: 0,
              },
              {
                backgroundColor: "#1A237E",
                label: "Actual deaths up to expected",
                data: this.deaths,
              },
              {
                backgroundColor: "#4CAF50",
                label: "Below expectation deaths",
                data: this.below_expectation_deaths,
              },
              {
                backgroundColor: "#F44336",
                label: "Excess deaths",
                data: this.above_expectation_deaths,
              },
            ],
          };
        });
      this.excess_deaths_request_successful = true;
    },
    get_yearly_deaths_data(geo_choice, age_choices, year_choice, max_week) {
      const backend_url = "<placeholder>/yearly_deaths";
      axios
        .post(backend_url, {
          "Geopolitical entity (reporting)": geo_choice,
          "Age class": age_choices,
          year: year_choice,
          max_week,
        })
        .then((res) => {
          this.labels = res.data.yearly_deaths.years;
          this.actual_deaths = res.data.yearly_deaths.actual_deaths;
          this.max_week = res.data.yearly_deaths.max_week;
          this.datacollection_yearly_deaths_chart = {
            labels: this.labels,
            datasets: [
              {
                backgroundColor: "#1A237E",
                label: "Yearly deaths",
                data: this.actual_deaths,
              },
            ],
          };
        });
      this.yearly_deaths_request_successful = true;
    },
  },
};
</script>
