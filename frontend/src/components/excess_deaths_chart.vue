<script>
import { Bar, mixins } from "vue-chartjs";

const { reactiveProp } = mixins;

export default {
  extends: Bar,

  mounted() {
    this.renderChart(this.chartData, this.options);
  },
  mixins: [reactiveProp],

  data: () => ({
    options: {
      scales: {
        yAxes: [
          {
            ticks: {
              beginAtZero: true,
            },
            gridLines: {
              display: true,
            },
            stacked: true,
          },
        ],
        xAxes: [
          {
            gridLines: {
              display: false,
            },
            stacked: true,
          },
        ],
      },
      legend: {
        display: true,
      },
      responsive: true,
      maintainAspectRatio: false,
    },
  }),
};
</script>
