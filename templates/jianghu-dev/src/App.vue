<script setup lang="ts">
import JianghuCard from './components/JianghuCard.vue'
</script>

<template>
  <JianghuCard />
</template>

<style>
@font-face {
  font-family: '峄山碑篆体';
  src: url('./assets/fonts/yishanbeizhuanti.ttf') format('truetype');
  font-weight: normal;
  font-style: normal;
}

* { margin: 0; padding: 0; box-sizing: border-box; }
html, body, #app {
  width: 100%;
  height: 100%;
  overflow: hidden;
}
</style>
