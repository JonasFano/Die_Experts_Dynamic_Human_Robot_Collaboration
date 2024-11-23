<script setup lang="ts">
import type { ChartDataset } from 'chart.js'


//todo: replace url API endpoints
const toggleText = () => {
  console.log('Toggling text');
  $fetch('http://localhost:5000/toggle_text');
}

const togglePoints = () => {
  console.log('Toggling points');
  $fetch('http://localhost:5000/toggle_points');
}

const toggleFixtures = () => {
  console.log('Toggling fixtures');
  $fetch('http://localhost:5000/toggle_fixtures');
}

const fetchData = async () => {
  try {
    const response = await $fetch('http://localhost:5000/data') as { heartRate: number, distance: number, stress: number };
    heartRate.value = response.heartRate;
    safetyDistance.value = response.distance;
    stressLevel.value = response.stress;
    addGraphDataPoint(stressLevel.value);
  } catch (error) {
    throw new Error('Failed to fetch data: ' + error);
  }
}

const graphData = ref<number[]>([])

const lineDatasets = computed<ChartDataset<'line'>[]>(() => [
  {
    data: graphData.value,
    borderColor: "#3182CE",
    backgroundColor: "rgb(49 130 206 / 60%)",
    borderWidth: 4,
    tension: 0.3,
    fill: true,
    animation: {
      duration: 100,
      easing: 'easeInOutQuad'
    }
  },
])

const addGraphDataPoint = (data: number) => {
  //const newData = Math.floor(Math.random() * 101) + 50; // Random number between 50 and 150
  graphData.value = [data, ...graphData.value].slice(0, 10); // Update the data and keep only the latest 10 points
};

onMounted(() => {
  setInterval(fetchData, 1000);
});

const safetyDistance = ref(0);
const heartRate = ref(0);
const stressLevel = ref(0);

</script>

<template >
  <div class="bg-gray-100 flex flex-col md:flex-row md:gap-8 min-h-screen">
    <div class="bg-gray-800 p-8 relative">
      <h1 class="font-bold text-4xl md:[writing-mode:vertical-lr] top-8 text-gray-500">Die Experts</h1>
    </div>
    <div class="flex flex-col gap-4 w-full md:mt-6 mr-8 p-4 md:p-0">
      <h2 class="text-2xl font-bold">Dashboard</h2>
      <div class="w-full flex flex-col md:flex-row gap-4">
        <KPICard title="Current heart rate" :value="heartRate" icon-name="heroicons:heart" />
        <KPICard title="Stress levels" :value="stressLevel" icon-name="heroicons:face-smile" />
        <KPICard title="Safety distance" :value="safetyDistance" icon-name="heroicons:exclamation-triangle" />
      </div>

      <div class="flex flex-col md:flex-row gap-4 w-full pb-12 md:pb-4">
        <div class="p-4 w-full flex flex-col gap-2 shadow bg-white rounded">
          <h2 class="font-bold">Live camera feed</h2>
          <Camera />
          <div class="flex gap-2">
            <Button @click="toggleText" text="Toggle text" />
            <Button @click="togglePoints" text="Toggle points" />
            <Button @click="toggleFixtures" text="Toggle fixtures" />
          </div>
        </div>

        <div class="p-4 w-full shadow bg-white rounded">
          <h2 class="font-bold mb-2">Stress Level</h2>
          <Graph :datasets="lineDatasets" />
        </div>
      </div>
    </div>
  </div>   
</template>

<style>
::selection {
  background-color: #3e4752; /* Replace #gray with your desired gray color, e.g., #d3d3d3 */
  color: white; /* Optional: set text color during selection */
}
</style>