<script setup lang="ts">
import { ref } from 'vue';
import { Line } from 'vue-chartjs';
import {
    ArcElement,
    Chart as ChartJS,
    Legend,
    Tooltip,
    CategoryScale,
    LinearScale,
    PointElement,
    LineElement,
    Filler,
} from 'chart.js';
import type { ChartOptions, ChartData, ChartDataset } from 'chart.js'


// Register Chart.js modules
ChartJS.register(ArcElement, Tooltip, Legend, CategoryScale, LinearScale, PointElement, LineElement, Filler);

const props = defineProps<{
  datasets: ChartDataset<'line'>[]
  labels?: string[]
}>()


const chartData = computed<ChartData<'line'>>(() => {
  return {
    labels: ["", "", "", "", "", "", "", "", "", ""],
    datasets: props.datasets,
  }
})

const chartOptions: ChartOptions<'line'> = {
  responsive: true,
  maintainAspectRatio: true,
  plugins: {
    legend: {
      display: false,
    },
  },
  scales: {
    y: {
      min: 0,
      max: 1
    },
  }
}

</script>

<template>
  <div>
    <Line
      :data="chartData"
      :options="chartOptions"
      height="200"
    />
  </div>
</template>
