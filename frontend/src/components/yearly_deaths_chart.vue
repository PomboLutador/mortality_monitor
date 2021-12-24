<script>
import { Bar, mixins } from 'vue-chartjs';

const { reactiveProp } = mixins;

export default {
  extends: Bar,

  mounted() {
    this.renderChart(this.chart_data, this.options);
  },
  mixins: [reactiveProp],

  data: () => ({
    options: {
      scales: {
        yAxes: [{
          ticks: {
            beginAtZero: true,
          },
          gridLines: {
            display: true,
          },
        }],
        xAxes: [{
          gridLines: {
            display: false,
          },
        }],
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
