<script setup>
import { computed } from 'vue';

/*
  Renders the student graph from GET /api/v1/student/graph
  { directed, nodes: [{ id: "Basic Arithmetic", level: "1" }], links: [{ source, target }] }

  Layout: topics are placed in columns by prerequisite depth (left to right).
  Assumes an edge source -> target means "source is a prerequisite of target".
*/
const props = defineProps({
  graph: { type: Object, required: true },
  // topic names that can be clicked (e.g. topics the student can be tested on)
  selectable: { type: Array, default: () => [] },
});
const emit = defineEmits(['select']);

const NODE_W = 170;
const NODE_H = 54;
const COL_GAP = 90;
const ROW_GAP = 26;
const PAD = 20;
const MAX_LEVEL = 3; // keep in sync with MAX_LEVEL in vidhyarthi.py

const layout = computed(() => {
  const nodes = props.graph?.nodes ?? [];
  const links = props.graph?.links ?? [];
  const ids = nodes.map((n) => n.id);
  const known = new Set(ids);

  // prerequisites of every node (only edges between nodes we actually have)
  const parents = {};
  ids.forEach((id) => (parents[id] = []));
  links.forEach((l) => {
    if (known.has(l.source) && known.has(l.target)) parents[l.target].push(l.source);
  });

  // depth = longest chain of prerequisites above the node
  const depth = {};
  const visiting = new Set();
  function depthOf(id) {
    if (depth[id] !== undefined) return depth[id];
    if (visiting.has(id)) return 0; // guards against accidental cycles
    visiting.add(id);
    const d = parents[id].length ? 1 + Math.max(...parents[id].map(depthOf)) : 0;
    visiting.delete(id);
    depth[id] = d;
    return d;
  }
  ids.forEach(depthOf);

  // group into columns
  const columns = {};
  ids.forEach((id) => (columns[depth[id]] ??= []).push(id));
  const colKeys = Object.keys(columns).map(Number);
  const maxDepth = colKeys.length ? Math.max(...colKeys) : 0;
  const maxRows = colKeys.length ? Math.max(...colKeys.map((k) => columns[k].length)) : 1;

  const height = PAD * 2 + maxRows * NODE_H + (maxRows - 1) * ROW_GAP;
  const width = PAD * 2 + (maxDepth + 1) * NODE_W + maxDepth * COL_GAP;

  const pos = {};
  colKeys.forEach((k) => {
    const col = columns[k];
    const colHeight = col.length * NODE_H + (col.length - 1) * ROW_GAP;
    const yStart = PAD + (height - PAD * 2 - colHeight) / 2;
    col.forEach((id, row) => {
      pos[id] = { x: PAD + k * (NODE_W + COL_GAP), y: yStart + row * (NODE_H + ROW_GAP) };
    });
  });

  const laidOutNodes = nodes.map((n) => ({
    id: n.id,
    level: Number(n.level) || 1, // backend sends level as a string
    x: pos[n.id].x,
    y: pos[n.id].y,
  }));

  const edges = links
    .filter((l) => known.has(l.source) && known.has(l.target))
    .map((l) => {
      const x1 = pos[l.source].x + NODE_W;
      const y1 = pos[l.source].y + NODE_H / 2;
      const x2 = pos[l.target].x;
      const y2 = pos[l.target].y + NODE_H / 2;
      const mid = (x1 + x2) / 2;
      return { key: `${l.source}->${l.target}`, d: `M ${x1} ${y1} C ${mid} ${y1}, ${mid} ${y2}, ${x2} ${y2}` };
    });

  return { nodes: laidOutNodes, edges, width, height };
});

function onNodeClick(id) {
  if (props.selectable.includes(id)) emit('select', id);
}
</script>

<template>
  <div class="graph">
    <div class="graph-scroll">
      <svg
        :viewBox="`0 0 ${layout.width} ${layout.height}`"
        :width="layout.width"
        :height="layout.height"
        role="img"
        aria-label="Your knowledge graph"
      >
        <defs>
          <marker
            id="graph-arrow"
            viewBox="0 0 10 10"
            refX="9"
            refY="5"
            markerWidth="7"
            markerHeight="7"
            orient="auto"
          >
            <path d="M 0 0 L 10 5 L 0 10 z" class="arrow-head" />
          </marker>
        </defs>

        <path
          v-for="e in layout.edges"
          :key="e.key"
          :d="e.d"
          class="edge"
          marker-end="url(#graph-arrow)"
        />

        <g
          v-for="n in layout.nodes"
          :key="n.id"
          class="node"
          :class="[`lvl-${n.level}`, { selectable: selectable.includes(n.id) }]"
          :transform="`translate(${n.x}, ${n.y})`"
          @click="onNodeClick(n.id)"
        >
          <rect :width="NODE_W" :height="NODE_H" rx="10" class="box" />
          <text :x="NODE_W / 2" y="23" text-anchor="middle" class="label">{{ n.id }}</text>
          <rect
            v-for="i in MAX_LEVEL"
            :key="i"
            :x="NODE_W / 2 - 38 + (i - 1) * 26"
            y="34"
            width="22"
            height="5"
            rx="2.5"
            class="pip"
            :class="{ on: i <= n.level }"
          />
        </g>
      </svg>
    </div>
    <p class="caption">Arrows lead from a prerequisite to the next topic. Fuller bars mean a higher level.</p>
  </div>
</template>

<style scoped>
.graph-scroll { overflow-x: auto; border: 1px solid #8884; border-radius: 12px; padding: 0.25rem; }
svg { display: block; max-width: none; margin: 0 auto; }

.edge { fill: none; stroke: #8889; stroke-width: 1.8; }
.arrow-head { fill: #8889; }

.box { fill: #3b82f61f; stroke: #3b82f6; stroke-width: 1.5; }
.lvl-2 .box { fill: #3b82f640; }
.lvl-3 .box { fill: #3b82f66b; }

.label { fill: currentColor; font-size: 14px; font-weight: 600; pointer-events: none; }
.pip { fill: #8884; }
.pip.on { fill: #3b82f6; }

.node.selectable { cursor: pointer; }
.node.selectable:hover .box { stroke-width: 2.5; }

.caption { opacity: 0.65; font-size: 0.8rem; margin: 0.5rem 0 0; }
</style>