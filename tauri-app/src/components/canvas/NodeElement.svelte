<script lang="ts">
  import type { NetworkNode } from "../../lib/types/network";
  import { currentTheme } from "../../lib/stores/uiStore";
  import { hostNodeIndices, pingAnimationStates } from "../../lib/stores/networkStore";
  import { settings } from "../../lib/stores/settingsStore";
  import squaredMetalUrl from "../../assets/textures/squared-metal.png";

  let {
    node,
    index,
    fillColor,
    outlineColor,
    outlineWidth,
    textColor,
    fontSize,
    onMouseDown,
    onMouseEnter,
    onMouseLeave,
    pingAnimationState = null,
  }: {
    node: NetworkNode;
    index: number;
    fillColor: string;
    outlineColor: string;
    outlineWidth: number;
    textColor: string;
    fontSize: number;
    onMouseDown: (e: MouseEvent) => void;
    onMouseEnter?: () => void;
    onMouseLeave?: () => void;
    pingAnimationState?: 'success' | 'failure' | null;
  } = $props();

  let isIronclad = $derived($currentTheme === "ironclad");
  let strobeDisabled = $derived($settings.disable_strobe_effects ?? false);
  let isHostNode = $derived($hostNodeIndices.has(index) && !strobeDisabled);
  let hasPingSuccess = $derived(pingAnimationState === 'success' && !strobeDisabled);
  let hasPingFailure = $derived(pingAnimationState === 'failure' && !strobeDisabled);

  // JS-driven filter animation state (cross-platform: works on WebKit/WebKitGTK)
  let filterStyle = $state('none');
  let _animRafId = 0;
  let _animCancel: (() => void) | null = null;

  function _cancelAnim() {
    if (_animCancel) { _animCancel(); _animCancel = null; }
    cancelAnimationFrame(_animRafId);
  }

  function _runAnim(
    frames: Array<{t: number, shadow: string}>,
    duration: number,
    keepLast = false
  ) {
    _cancelAnim();
    const start = performance.now();
    let cancelled = false;
    function lerp(a: number, b: number, t: number) { return a + (b - a) * t; }
    function lerpShadow(s1: string, s2: string, t: number) {
      const re = /drop-shadow\(0 0 ([\d.]+)px rgba\(([\d, ]+),([\d.]+)\)\)/;
      const m1 = s1.match(re), m2 = s2.match(re);
      if (!m1 || !m2) return t < 0.5 ? s1 : s2;
      const blur = lerp(+m1[1], +m2[1], t);
      const alpha = lerp(+m1[3], +m2[3], t);
      return `drop-shadow(0 0 ${blur.toFixed(2)}px rgba(${m1[2]},${alpha.toFixed(3)}))`;
    }
    function step(now: number) {
      if (cancelled) return;
      const p = Math.min((now - start) / duration, 1);
      let fi = 0;
      for (let i = 0; i < frames.length - 1; i++) {
        if (p >= frames[i].t) fi = i;
      }
      const f0 = frames[fi], f1 = frames[Math.min(fi + 1, frames.length - 1)];
      const segLen = f1.t - f0.t;
      const localT = segLen > 0 ? (p - f0.t) / segLen : 1;
      filterStyle = lerpShadow(f0.shadow, f1.shadow, localT);
      if (p < 1) {
        _animRafId = requestAnimationFrame(step);
      } else {
        filterStyle = keepLast ? frames[frames.length - 1].shadow : 'none';
        _animCancel = null;
      }
    }
    _animRafId = requestAnimationFrame(step);
    _animCancel = () => { cancelled = true; filterStyle = 'none'; };
  }

  // Ping animation effect — drives JS animation and auto-clears state
  $effect(() => {
    if (hasPingSuccess) {
      _runAnim([
        { t: 0,    shadow: 'drop-shadow(0 0 0px rgba(39, 174, 96, 0))' },
        { t: 0.15, shadow: 'drop-shadow(0 0 22px rgba(39, 174, 96, 0.9))' },
        { t: 0.40, shadow: 'drop-shadow(0 0 12px rgba(39, 174, 96, 0.4))' },
        { t: 1,    shadow: 'drop-shadow(0 0 0px rgba(39, 174, 96, 0))' },
      ], 1000);
      const id = setTimeout(() => {
        pingAnimationStates.update((s) => { const c = { ...s }; delete c[index]; return c; });
      }, 1000);
      return () => clearTimeout(id);
    } else if (hasPingFailure) {
      _runAnim([
        { t: 0,    shadow: 'drop-shadow(0 0 0px rgba(231, 76, 60, 0))' },
        { t: 0.30, shadow: 'drop-shadow(0 0 22px rgba(231, 76, 60, 0.9))' },
        { t: 0.55, shadow: 'drop-shadow(0 0 12px rgba(231, 76, 60, 0.4))' },
        { t: 1,    shadow: 'drop-shadow(0 0 0px rgba(231, 76, 60, 0))' },
      ], 1200);
      const id = setTimeout(() => {
        pingAnimationStates.update((s) => { const c = { ...s }; delete c[index]; return c; });
      }, 1200);
      return () => clearTimeout(id);
    }
  });

  // Host node strobe — only runs when no ping animation is active
  $effect(() => {
    if (isHostNode && !hasPingSuccess && !hasPingFailure) {
      _runAnim([
        { t: 0,      shadow: 'drop-shadow(0 0 8px rgba(255, 255, 0, 0.2))' },
        { t: 0.1667, shadow: 'drop-shadow(0 0 16px rgba(255, 255, 0, 0.8))' },
        { t: 0.3333, shadow: 'drop-shadow(0 0 8px rgba(255, 255, 0, 0.2))' },
        { t: 0.50,   shadow: 'drop-shadow(0 0 16px rgba(255, 255, 0, 0.8))' },
        { t: 0.6667, shadow: 'drop-shadow(0 0 8px rgba(255, 255, 0, 0.2))' },
        { t: 0.8333, shadow: 'drop-shadow(0 0 16px rgba(255, 255, 0, 0.8))' },
        { t: 1,      shadow: 'drop-shadow(0 0 8px rgba(255, 255, 0, 0.5))' },
      ], 6000, true);
    } else if (!isHostNode && !hasPingSuccess && !hasPingFailure) {
      _cancelAnim();
    }
  });

  // Approximate text width for sizing the rectangle
  let textEl: SVGTextElement;
  let textWidth = $state(30);
  let textHeight = $state(16);

  $effect(() => {
    if (textEl) {
      // Force re-measure when name or fontSize changes
      const _ = node.name;
      const __ = fontSize;
      requestAnimationFrame(() => {
        if (textEl) {
          try {
            const bbox = textEl.getBBox();
            textWidth = bbox.width;
            textHeight = bbox.height;
          } catch {
            // getBBox can fail if element is not rendered
          }
        }
      });
    }
  });

  let pad = $derived(Math.max(2, Math.round(fontSize * 0.3)));
  let halfW = $derived(textWidth / 2 + pad);
  let halfH = $derived(textHeight / 2 + pad);
</script>

<!-- svelte-ignore a11y_no_static_element_interactions -->
<g
  data-type="node"
  data-index={index}
  style:filter={filterStyle}
  style:cursor="pointer"
  onmousedown={onMouseDown}
  onmouseenter={onMouseEnter}
  onmouseleave={onMouseLeave}
>
  {#if isIronclad}
    <defs>
      <pattern id="node-texture-{index}" patternUnits="userSpaceOnUse" width="132" height="132">
        <image href={squaredMetalUrl} width="132" height="132" opacity="0.12" />
      </pattern>
    </defs>
  {/if}
  <!-- Main node rect -->
  <rect
    x={node.x - halfW}
    y={node.y - halfH}
    width={halfW * 2}
    height={halfH * 2}
    fill={fillColor}
    stroke={outlineColor}
    stroke-width={isIronclad ? Math.max(outlineWidth, 2) : outlineWidth}
    rx={isIronclad ? 3 : 2}
  />
  {#if isIronclad}
    <!-- Texture overlay on node -->
    <rect
      x={node.x - halfW}
      y={node.y - halfH}
      width={halfW * 2}
      height={halfH * 2}
      fill="url(#node-texture-{index})"
      stroke="none"
      rx="3"
      pointer-events="none"
    />
    <!-- Top highlight edge -->
    <line
      x1={node.x - halfW + 3}
      y1={node.y - halfH + 1}
      x2={node.x + halfW - 3}
      y2={node.y - halfH + 1}
      stroke="rgba(255,255,255,0.15)"
      stroke-width="1"
      pointer-events="none"
    />
    <!-- Bottom shadow edge -->
    <line
      x1={node.x - halfW + 3}
      y1={node.y + halfH - 1}
      x2={node.x + halfW - 3}
      y2={node.y + halfH - 1}
      stroke="rgba(0,0,0,0.4)"
      stroke-width="1"
      pointer-events="none"
    />
  {/if}
  <text
    bind:this={textEl}
    x={node.x}
    y={node.y}
    text-anchor="middle"
    dominant-baseline="central"
    fill={textColor}
    font-family={isIronclad ? "DM Sans, Helvetica, Arial, sans-serif" : "Helvetica, Arial, sans-serif"}
    font-size={fontSize}
    font-weight={isIronclad ? "500" : "normal"}
    pointer-events="none"
  >
    {node.name}
  </text>
</g>
