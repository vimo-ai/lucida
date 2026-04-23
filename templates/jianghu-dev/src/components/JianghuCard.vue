<script setup lang="ts">
import { ref, onMounted } from 'vue'
import { generateStampAsync } from '@jobinjia/shuimo-core'
import { XuanPaper, GoldFleckColors } from '@jobinjia/shuimo-core'
import InkRadar from './InkRadar.vue'
import { DATA } from '../data'
import stampFontUrl from '../assets/fonts/yishanbeizhuanti.ttf'

const stampSvg = ref('')
const paperBg = ref('')

const CN = '零壹贰叁肆伍陆柒捌玖'
function toCnNum(n: number): string {
  n = Math.round(n)
  if (n === 100) return '壹佰'
  if (n < 10) return CN[n]
  const tens = Math.floor(n / 10)
  const ones = n % 10
  return CN[tens] + '拾' + (ones ? CN[ones] : '')
}

async function waitForFont(family: string, size: number) {
  const fontSpec = `${size}px ${family}`
  for (let i = 0; i < 20; i++) {
    if (document.fonts.check(fontSpec)) return
    try { await document.fonts.load(fontSpec) } catch {}
    if (document.fonts.check(fontSpec)) return
    await new Promise(r => setTimeout(r, 100))
  }
}

onMounted(async () => {
  // Generate xuan paper with gold flecks
  const dataUrl = XuanPaper.generateDataURL({
    width: 512,
    height: 512,
    baseColor: [245, 238, 225],
    goldFlecks: true,
    goldDensity: 0.3,
    goldSize: [1, 4],
    goldColor: GoldFleckColors.gold,
    goldClustering: 0.6,
    seed: 42,
  })
  paperBg.value = dataUrl

  // Wait for stamp font to load
  await document.fonts.ready
  await waitForFont('峄山碑篆体', 48)

  // Generate yang stamp (阳章)
  const svg = await generateStampAsync({
    text: DATA.stampText,
    type: 'yin',
    shape: 'square',
    color: '#C8102E',
    fontFamily: '峄山碑篆体',
    fontUrl: stampFontUrl,
    fontSize: 48,
    seed: 42,
    noiseAmount: 0.12,
    textCarving: 'stone-cut',
  })
  stampSvg.value = svg
})
</script>

<template>
  <div class="page" :style="paperBg ? { backgroundImage: `url(${paperBg})` } : {}">
    <!-- Rice paper fiber texture over gold flecks -->
    <div class="rice-paper-overlay" />

    <!-- Header -->
    <header class="header">
      <div class="header-left">
        <h1 class="sect-name">「{{ DATA.sect }}」</h1>
        <span class="rank-tag">
          <span class="rank-text">{{ DATA.rank }}</span>
          <span class="match-score">契合 · {{ toCnNum(DATA.matchScore) }}</span>
        </span>
      </div>
      <div class="stamp-right" v-html="stampSvg" />
    </header>
    <div class="divider-h" />

    <!-- Main content -->
    <main class="content">
      <!-- Left: Radar + Summary -->
      <div class="chart-area">
        <InkRadar :dimensions="DATA.dimensions" :size="540" class="radar" />
        <div class="summary">{{ DATA.summary }}</div>
      </div>

      <!-- Right: Dimensions list -->
      <div class="dims-list">
        <div
          v-for="dim in DATA.dimensions"
          :key="dim.key"
          class="dim-row"
        >
          <div class="dim-score" :style="{ color: dim.color }">{{ dim.score }}</div>
          <div class="dim-info">
            <div class="dim-name" :style="{ color: dim.color }">{{ dim.name }}</div>
            <div class="dim-tagline">{{ dim.tagline }}</div>
            <div class="dim-data" v-html="dim.data"></div>
          </div>
        </div>
      </div>
    </main>

    <div class="divider-h" />
    <!-- Footer -->
    <footer class="footer">
      <div class="stats">
        <div v-for="(stat, i) in DATA.stats" :key="i" class="stat">
          <span class="stat-value">{{ stat.value }}</span>
          <span class="stat-unit">{{ stat.unit }}</span>
        </div>
      </div>
      <div class="footer-credit">{{ DATA.credit }}</div>
    </footer>

  </div>
</template>

<style scoped>
@import url('https://fonts.googleapis.com/css2?family=Noto+Serif+SC:wght@300;500;700&family=IBM+Plex+Mono:wght@400;500;600&display=swap');

@font-face {
  font-family: 'WLJH';
  src: url('../assets/fonts/wljh.ttf') format('truetype');
  font-weight: normal;
  font-style: normal;
}

.page {
  width: 100vw;
  height: 100vh;
  display: grid;
  grid-template-rows: auto auto 1fr auto auto;
  padding: 2rem 2.5rem;
  background-color: #f4ede0;
  background-repeat: repeat;
  color: #3a3530;
  font-family: 'Noto Serif SC', serif;
  position: relative;
  overflow: hidden;
}

.rice-paper-overlay {
  position: absolute;
  top: 0;
  left: 0;
  width: 100%;
  height: 100%;
  background-image: url('../assets/rice-paper.webp');
  background-repeat: repeat;
  opacity: 0.6;
  pointer-events: none;
  z-index: 0;
  mix-blend-mode: multiply;
}

.page > *:not(.rice-paper-overlay):not(.stamp) {
  position: relative;
  z-index: 1;
}

.divider-h {
  width: 100%;
  height: 5px;
  background: url('../assets/crossrange.webp') repeat-x;
  margin: 0.6rem 0;
}

/* Header */
.header {
  display: flex;
  align-items: center;
  justify-content: space-between;
  padding-bottom: 1rem;
}

.header-left {
  display: flex;
  align-items: baseline;
  gap: 1rem;
}

.sect-name {
  font-family: 'WLJH', serif;
  font-size: 2.8rem;
  font-weight: 700;
  letter-spacing: 0.05em;
  color: #2a2520;
}

.rank-tag {
  display: flex;
  align-items: baseline;
  gap: 0.5rem;
}

.rank-text {
  font-family: 'WLJH', serif;
  font-size: 1.6rem;
  color: #8b2252;
  font-weight: 600;
}

.match-score {
  font-size: 1rem;
  color: #8a8078;
  font-family: 'IBM Plex Mono', monospace;
}

/* Content */
.content {
  display: grid;
  grid-template-columns: 55% 45%;
  gap: 1.5rem;
  min-height: 0;
  overflow: hidden;
}

.chart-area {
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  min-height: 0;
  overflow: hidden;
}

.radar {
  width: 45%;
  height: auto;
  flex-shrink: 1;
}

.summary {
  font-family: 'Kaiti SC', 'STKaiti', 'KaiTi', serif;
  font-size: 1.2rem;
  line-height: 2;
  color: #5a5550;
  padding: 0 0.6rem;
  margin-top: 1rem;
  overflow: hidden;
}

/* Dimensions list */
.dims-list {
  display: flex;
  flex-direction: column;
  justify-content: space-evenly;
  padding-left: 1.5rem;
  background: url('../assets/vertical.webp') repeat-y left top;
  background-size: 6px auto;
  min-height: 0;
  overflow: hidden;
}

.dim-row {
  display: grid;
  grid-template-columns: 3.5rem 1fr;
  gap: 0.75rem;
  align-items: baseline;
}

.dim-score {
  font-family: 'WLJH', serif;
  font-size: 2.8rem;
  font-weight: 700;
  line-height: 1;
  text-align: right;
  color: #5a4a40;
}

.dim-info {
  display: flex;
  flex-direction: column;
  gap: 1px;
}

.dim-name {
  font-family: 'WLJH', serif;
  font-size: 1.35rem;
  font-weight: 700;
  color: #3a3530;
}

.dim-tagline {
  font-family: 'Kaiti SC', 'STKaiti', 'KaiTi', serif;
  font-size: 1.1rem;
  color: #8a8078;
}

.dim-data {
  font-family: 'IBM Plex Mono', monospace;
  font-size: 0.95rem;
  color: #a09890;
}

.dim-data :deep(strong) {
  font-weight: 600;
  color: #5a5550;
}

/* Footer */
.footer {
  display: flex;
  align-items: baseline;
  justify-content: space-between;
  padding-top: 1rem;
}

.stats {
  display: flex;
  gap: 2rem;
}

.stat {
  display: flex;
  align-items: baseline;
  gap: 0.2rem;
}

.stat-value {
  font-family: 'Kaiti SC', 'STKaiti', 'KaiTi', serif;
  font-size: 1.6rem;
  font-weight: 700;
  color: #2a2520;
}

.stat-unit {
  font-family: 'WLJH', serif;
  font-size: 0.95rem;
  color: #8a8078;
  letter-spacing: 0.05em;
}

.footer-credit {
  font-family: 'WLJH', serif;
  font-size: 0.85rem;
  color: #a09890;
}

/* Stamp */
.stamp-right {
  display: flex;
  align-items: center;
  justify-content: center;
  width: 4.5rem;
  height: 4.5rem;
  flex-shrink: 0;
  opacity: 0.85;
}

.stamp-right :deep(svg) {
  width: 100%;
  height: 100%;
}


</style>
