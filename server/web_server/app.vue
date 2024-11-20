<script setup lang="ts">


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

const graphData = ref<number[]>([])

const lineDatasets = computed<ChartDataset<'line'>[]>(() => [
  {
    data: graphData.value,
    borderColor: "#3182CE",
    backgroundColor: "#3182CE",
    borderWidth: 4,
    tension: 0.3,
    fill: true,
  },
])

const addDataPoint = () => {
    const newData = Math.floor(Math.random() * 101) + 50; // Random number between 50 and 150
    graphData.value = [...graphData.value, newData]; // Update the data
};
</script>

<template >
  <div class="p-4">
    <h1 class="font-bold text-2xl">Die Experts</h1>

    <div class="flex gap-4 w-full">
      <div class="border p-4 w-full">
        <h2>Live camera feed</h2>
        <Camera />
        <Button @click="toggleText" text="Toggle text" />
        <Button @click="togglePoints" text="Toggle points" />
        <Button @click="toggleFixtures" text="Toggle fixtures" />
      </div>

      <div class="border p-4 w-full">
        <h2>Live heart rate data</h2>
        <Graph :datasets="lineDatasets" />
        <Button @click="addDataPoint" text="Add datapoint" />
        <p>{{ graphData }}</p>
      </div>
    </div>
    
   
  </div>
</template>
