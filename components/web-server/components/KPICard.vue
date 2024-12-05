<script setup lang="ts">
    defineProps<{
        title: string,
        value: number | string,
        iconName: string
    }>();
</script>

<template>
  <div class="p-4 shadow rounded bg-white min-w-[200px]">
    <h3 class="text-gray-500">{{ title }}</h3>
    <div class="flex gap-1 text-3xl">
        <Icon :name="iconName" size="20" class="translate-y-1/2" />
        <span v-if="typeof value === 'number'" class="font-semibold"> {{ value.toFixed(2) }}</span>
        <span v-if="typeof value === 'string'" class="font-semibold"> {{ value }}</span>
    </div>
  </div>
</template>