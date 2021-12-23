<script>
import { Bar, mixins } from 'vue-chartjs';
import zoom from 'chartjs-plugin-zoom';

const { reactiveProp } = mixins;

export default {
  extends: Bar,

  mounted() {
    this.addPlugin(zoom);
    this.renderChart(this.chartData, this.options);
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
