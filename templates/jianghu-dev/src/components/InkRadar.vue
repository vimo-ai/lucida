<script setup lang="ts">
import { computed } from 'vue'
import { Brush } from '@jobinjia/shuimo-core'
import type { Dimension } from '../data'

const props = defineProps<{
  dimensions: Dimension[]
  size?: number
}>()

const size = computed(() => props.size ?? 540)
const cx = computed(() => size.value / 2)
const cy = computed(() => size.value / 2)
const R = computed(() => size.value * 0.35)
const n = computed(() => props.dimensions.length)

function angle(i: number): number {
  return (2 * Math.PI * i / n.value) - Math.PI / 2
}

function pos(i: number, r: number): [number, number] {
  const a = angle(i)
  return [cx.value + r * Math.cos(a), cy.value + r * Math.sin(a)]
}

function interpolateLine(from: [number, number], to: [number, number], steps: number): [number, number][] {
  const pts: [number, number][] = []
  for (let i = 0; i <= steps; i++) {
    const t = i / steps
    pts.push([from[0] + t * (to[0] - from[0]), from[1] + t * (to[1] - from[1])])
  }
  return pts
}

// Grid rings with brush strokes
const gridSvg = computed(() => {
  let svg = ''
  const rings = [0.33, 0.66, 1.0]

  for (const pct of rings) {
    const r = R.value * pct
    for (let i = 0; i < n.value; i++) {
      const from = pos(i, r)
      const to = pos((i + 1) % n.value, r)
      const pts = interpolateLine(from, to, 8)
      svg += Brush.stroke(pts, {
        width: pct === 1.0 ? 1.5 : 0.8,
        color: 'rgba(80,70,60,0.25)',
        noise: 0.3,
        flyingWhite: 0.1,
        inkStart: 0.4,
        inkEnd: 0.3,
        texture: 0,
      })
    }
  }
  return svg
})

// Axis lines from center to vertices
const axisSvg = computed(() => {
  let svg = ''
  for (let i = 0; i < n.value; i++) {
    const to = pos(i, R.value)
    const pts = interpolateLine([cx.value, cy.value], to, 8)
    svg += Brush.stroke(pts, {
      width: 0.6,
      color: 'rgba(80,70,60,0.15)',
      noise: 0.2,
      flyingWhite: 0.05,
      inkStart: 0.2,
      inkEnd: 0.3,
      texture: 0,
    })
  }
  return svg
})

// Data polygon with brush edges
const dataSvg = computed(() => {
  let svg = ''
  const dataPoints = props.dimensions.map((d, i) => pos(i, R.value * d.score / 100))

  // Filled area — ink wash style
  const fillPath = dataPoints.map((p, i) => `${i === 0 ? 'M' : 'L'}${p[0].toFixed(2)},${p[1].toFixed(2)}`).join(' ') + ' Z'
  svg += `<path d="${fillPath}" fill="rgba(80,50,30,0.08)" stroke="none" />`

  // Brush stroke edges
  for (let i = 0; i < dataPoints.length; i++) {
    const from = dataPoints[i]
    const to = dataPoints[(i + 1) % dataPoints.length]
    const pts = interpolateLine(from, to, 6)
    svg += Brush.stroke(pts, {
      width: 2,
      color: 'rgba(60,40,30,0.5)',
      noise: 0.4,
      flyingWhite: 0.15,
      inkStart: 0.7,
      inkEnd: 0.5,
      texture: 1,
    })
  }

  // Vertex dots
  dataPoints.forEach((p) => {
    svg += Brush.dot(p[0], p[1], {
      width: 5,
      color: `rgba(80,40,30,0.7)`,
      noise: 0.5,
    })
  })

  return svg
})

// Labels
const labels = computed(() => {
  return props.dimensions.map((d, i) => {
    const a = angle(i)
    const cosA = Math.cos(a)
    const sinA = Math.sin(a)
    const lp = pos(i, R.value + 30)
    const yShift = sinA * 10

    let anchor = 'middle'
    if (cosA > 0.25) anchor = 'start'
    else if (cosA < -0.25) anchor = 'end'

    return {
      x: lp[0],
      scoreY: lp[1] + yShift - 8,
      nameY: lp[1] + yShift + 12,
      anchor,
      score: d.score,
      name: d.name,
      color: d.color,
    }
  })
})
</script>

<template>
  <svg
    :viewBox="`0 0 ${size} ${size}`"
    :width="size"
    :height="size"
    xmlns="http://www.w3.org/2000/svg"
    class="ink-radar"
  >
    <!-- Grid rings -->
    <g v-html="gridSvg" />
    <!-- Axis lines -->
    <g v-html="axisSvg" />
    <!-- Data polygon -->
    <g v-html="dataSvg" />
    <!-- Labels -->
    <template v-for="label in labels" :key="label.name">
      <text
        :x="label.x"
        :y="label.scoreY"
        :text-anchor="label.anchor"
        dominant-baseline="central"
        :fill="label.color"
        font-family="'WLJH', 'Noto Serif SC', serif"
        font-size="17"
        font-weight="700"
      >{{ label.score }}</text>
      <text
        :x="label.x"
        :y="label.nameY"
        :text-anchor="label.anchor"
        dominant-baseline="central"
        :fill="label.color"
        font-family="'WLJH', 'Noto Serif SC', serif"
        font-size="13"
        font-weight="500"
        opacity="0.7"
      >{{ label.name }}</text>
    </template>
  </svg>
</template>

<style scoped>
.ink-radar {
  flex-shrink: 1;
  min-height: 0;
}
</style>
