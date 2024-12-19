<script setup lang="ts">
defineProps<{
    text: string
}>()
</script>
<template>
      <button class="py-2 px-4 border rounded bg-gray-100 hover:bg-gray-200">{{ text }}</button>
</template>