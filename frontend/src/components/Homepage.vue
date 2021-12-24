<template>
  <v-container>
    <v-row class="text-center mt-5">
      <v-col cols="3">
        <h2 class="text-left">Welcome</h2>
        <p class="text-justify">
          This website allows tracking of all-cause mortality in various age
          groups on a weekly basis for a variety of European countries.
        </p>
      </v-col>
      <v-col cols="1"></v-col>
      <v-col cols="2">
        <v-select
          v-model="country_selection"
          :items="geo_options"
          item-value="name"
          item-text="name"
          label="Region"
          outlined
        ></v-select>
      </v-col>
      <v-col cols="3">
        <v-container fluid>
          <v-select
            v-model="age_groups_selection"
            :items="available_age_groups"
            label="Age groups"
            item-text="name"
            item-value="value"
            multiple
          ></v-select>
          <v-btn
            @click="
              get_excess_deaths_data(country_selection, age_groups_selection, year_selection);
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
            >Draw plot</v-btn
          >
        </v-container>
      </v-col>

      <v-col cols="1">
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
    <v-row class="text-left">
      <v-col cols="3">
        <h2>Methodology</h2>
        <p>
          Weekly mortality data is pulled from EUROSTAT's <i>demo_r_mweek3</i> table.
          To compute expected deaths for a given weekly period <b>p</b>, the average of the 3 previous datapoints 
          with the same calendar week is computed. Datapoints not within mean +- standard deviation are
          disregarded. 
          <br>
          <br>
          A linear regression is fit through the prior 3 years of yearly deaths, starting from <b>p - 104 weeks</b>
          to <b>p - 52 weeks</b>. The growth of that linear regression is applied to the above calculated mean of
          previous observations to arrive at the expectation value for <b>p</b>.
          <br>
          <br>
          The model to compute the epxected deaths thus has an effective forecasting horizon of 52 weeks.
        </p>
      </v-col>
      <v-col cols="1"> </v-col>
      <v-col class="mb-4" cols="7">
        <h1 v-if="
          (available_geos_query_is_successful == null) && 
          (available_ages_query_is_successful == null) && 
          (available_years_query_is_successful == null)">
          Please wait while the data is being fetched
        </h1>
        <v-overlay v-if="
          (available_geos_query_is_successful == null) && 
          (available_ages_query_is_successful == null) && 
          (available_years_query_is_successful == null)"></v-overlay>
        <v-progress-linear
          indeterminate
          color="primary"
          v-if="
            (available_geos_query_is_successful == null) && 
            (available_ages_query_is_successful == null) && 
            (available_years_query_is_successful == null)"
        ></v-progress-linear>
        <h2 v-if="excess_deaths_request_successful" class="font-weight-bold mb-3 text-center">
          All-cause mortality chart for country {{ country_selection }}
        </h2>
        <excess_deaths_chart
          v-if="excess_deaths_request_successful"
          :chart_data="datacollection_excess_deaths_chart"
          class="mt-3"
        ></excess_deaths_chart>
      </v-col>
      <v-col cols="1"> </v-col>
    </v-row>
    <v-row class="text-left">
      <v-col cols="3">
      </v-col>
      <v-col cols="1"> </v-col>
      <v-col cols="7">
        <h2 v-if="yearly_deaths_request_successful" class="text-center font-weight-bold mb-3">
          Aggregated yearly deaths for country
          {{ country_selection }} until calendar week {{ calendar_week_selection }}
        </h2>
        <h6 v-if="yearly_deaths_request_successful" class="text-center font-weight-bold mb-3">
        <i>(If current year hasn't passed calendar week {{ calendar_week_selection }} yet, all available data for that year is considered.)</i>
        </h6>
        <yearly_deaths_chart
          v-if="yearly_deaths_request_successful"
          :chart_data="datacollection_yearly_deaths_chart"
        ></yearly_deaths_chart>
      </v-col>
      <v-col cols="1"> </v-col>
    </v-row>
  </v-container>
</template>

<script>
import axios from "axios";
import excess_deaths_chart from "./excess_deaths_chart.vue";
import yearly_deaths_chart from "./yearly_deaths_chart.vue";

export default {
  name: "Homepage",

  data: () => ({
    // Query flags
    excess_deaths_request_successful: null,
    yearly_deaths_request_successful: null,
    available_geos_query_is_successful: null,
    available_ages_query_is_successful: null,
    available_years_query_is_successful: null,

    // UI selections
    calendar_week_selection: 53,
    year_selection: null,
    country_selection: "",
    age_groups_selection: "",

    // UI options
    calendar_week_options: Array.from({ length: 53 }, (x, i) => i + 1),
    geo_options: [],
    available_age_groups: {},
    available_years: [],
    
    // Chart data
    labels: [],
    datacollection_excess_deaths_chart: {},
    datacollection_yearly_deaths_chart: {},
  }),

  components: {
    "excess_deaths_chart": excess_deaths_chart,
    "yearly_deaths_chart": yearly_deaths_chart,
  },

  mounted() {
    // Get available geos
    const available_geos_url = "http://<placeholder>/available_geos";
    axios
      .get(available_geos_url, {},
      )
      .then((res) => {
        this.geo_options = res.data.sort();
        this.available_geos_query_is_successful = true;
      })
      .catch((error) => {
        console.error(error);
      });

    // Get available age groups
    const available_ages_url = "http://<placeholder>/available_ages";
    axios
      .get(available_ages_url, {},)
      .then((res) => {
      this.available_age_groups = Object.entries(res.data).map((arr) => ({
        name: arr[1],
        value: arr[0],}));
      this.available_ages_query_is_successful = true;
      })
      .catch((error) => {
        console.error(error);
      });

    // Get available years
    const available_years_url = "http://<placeholder>/available_years";
    axios
      .get(available_years_url, {},)
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
      const backend_url = "http://<placeholder>/excess_deaths";
      axios
        .post(backend_url, {
            geo: geo_choice,
            age: age_choices,
            year: year_choice,
          },
        )
        .then((res) => {
          this.labels = res.data.label;
          this.deaths = res.data.deaths;
          this.excess_deaths = res.data.excess_deaths;
          this.expected_deaths = res.data.expected_deaths;
          this.above_expectation_deaths =
            res.data.above_expectation_deaths;
          this.below_expectation_deaths =
            res.data.below_expectation_deaths;
          this.datacollection_excess_deaths_chart = {
            labels: this.labels,
            datasets: [
              {
                pointBackgroundColor: "#000000",
                pointBorderColor: "#000000",
                borderWidth: 1,
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
                backgroundColor: "#F44336",
                label: "Excess deaths",
                data: this.above_expectation_deaths,
              },
              {
                backgroundColor: "#4CAF50",
                label: "Below expectation deaths",
                data: this.below_expectation_deaths,
              },
              {
                backgroundColor: "#1A237E",
                label: "Actual deaths",
                data: this.deaths,
              },
            ],
          };
        });
      this.excess_deaths_request_successful = true;
    },
    get_yearly_deaths_data(geo_choice, age_choices, year_choice, max_week) {
      const backend_url = "http://<placeholder>/yearly_deaths";
      axios
        .post(backend_url, {
            geo: geo_choice,
            age: age_choices,
            year: year_choice,
            max_week: max_week,
          },
        )
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
