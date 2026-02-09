<script lang="ts">
  import { isDark, activeDialog } from "../../lib/stores/uiStore";
  import { getThemeColors } from "../../lib/theme/colors";
  import type { Snippet } from "svelte";

  let {
    title,
    width = 400,
    onClose,
    children,
  }: {
    title: string;
    width?: number;
    onClose?: () => void;
    children: Snippet;
  } = $props();

  let colors = $derived(getThemeColors($isDark));

  // Drag state
  let isDragging = $state(false);
  let dragStartX = 0;
  let dragStartY = 0;
  let posX = $state(-1);
  let posY = $state(-1);
  let dialogEl: HTMLDivElement;

  function close() {
    if (onClose) {
      onClose();
    } else {
      activeDialog.set(null);
    }
  }

  function onTitleMouseDown(e: MouseEvent) {
    isDragging = true;
    dragStartX = e.clientX - posX;
    dragStartY = e.clientY - posY;

    const onMove = (me: MouseEvent) => {
      if (isDragging) {
        posX = me.clientX - dragStartX;
        posY = me.clientY - dragStartY;
      }
    };

    const onUp = () => {
      isDragging = false;
      window.removeEventListener("mousemove", onMove);
      window.removeEventListener("mouseup", onUp);
    };

    window.addEventListener("mousemove", onMove);
    window.addEventListener("mouseup", onUp);
  }

  function handleKeydown(e: KeyboardEvent) {
    if (e.key === "Escape") {
      close();
    }
  }

  // Center on mount
  import { onMount } from "svelte";
  onMount(() => {
    if (dialogEl && posX === -1) {
      const rect = dialogEl.getBoundingClientRect();
      posX = (window.innerWidth - rect.width) / 2;
      posY = (window.innerHeight - rect.height) / 2;
    }
  });
</script>

<svelte:window onkeydown={handleKeydown} />

<!-- Backdrop -->
<!-- svelte-ignore a11y_no_static_element_interactions -->
<div
  class="fixed inset-0 z-40"
  style:background-color="rgba(0,0,0,0.3)"
  onclick={close}
></div>

<!-- Dialog -->
<div
  bind:this={dialogEl}
  class="fixed z-50 rounded shadow-xl overflow-hidden"
  style:left="{posX}px"
  style:top="{posY}px"
  style:width="{width}px"
  style:border="2px solid {colors.BORDER_COLOR}"
  style:background-color={colors.FRAME_BG}
  onclick={(e) => e.stopPropagation()}
>
  <!-- Title bar -->
  <!-- svelte-ignore a11y_no_static_element_interactions -->
  <div
    class="flex items-center justify-between px-3 py-2 cursor-move select-none"
    style:background-color={colors.FRAME_BG}
    style:border-bottom="1px solid {colors.BORDER_COLOR}"
    onmousedown={onTitleMouseDown}
  >
    <span
      class="text-sm font-medium"
      style:color={colors.BUTTON_TEXT}
    >
      {title}
    </span>
    <button
      class="text-sm px-2 py-0.5 rounded hover:opacity-70"
      style:color={colors.BUTTON_TEXT}
      style:background-color={colors.FRAME_BG}
      onclick={close}
    >
      X
    </button>
  </div>

  <!-- Content -->
  <div
    class="p-4 overflow-auto"
    style:max-height="80vh"
    style:background-color={colors.FRAME_BG}
  >
    {@render children()}
  </div>
</div>
