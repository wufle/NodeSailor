<script lang="ts">
  import type { Snippet } from "svelte";
  import { currentTheme } from "../../lib/stores/uiStore";

  let {
    text,
    children,
  }: {
    text: string;
    children: Snippet;
  } = $props();

  let isIronclad = $derived($currentTheme === "ironclad");
  let show = $state(false);
  let x = $state(0);
  let y = $state(0);

  function onMouseEnter(e: MouseEvent) {
    show = true;
    x = e.clientX + 10;
    y = e.clientY + 10;
  }

  function onMouseLeave() {
    show = false;
  }
</script>

<!-- svelte-ignore a11y_no_static_element_interactions -->
<span
  onmouseenter={onMouseEnter}
  onmouseleave={onMouseLeave}
>
  {@render children()}
</span>

{#if show}
  <div
    class="fixed z-50 px-2 py-1 text-xs rounded pointer-events-none {isIronclad ? 'ironclad-tooltip' : 'shadow bg-gray-800 text-white'}"
    style:left="{x}px"
    style:top="{y}px"
  >
    {text}
  </div>
{/if}
