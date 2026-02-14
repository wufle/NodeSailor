<script lang="ts">
  import { zoom, panX, panY, isDark, currentTheme, zoomPercent } from "../../lib/stores/uiStore";
  import { effectiveColors } from "../../lib/theme/colors";

  let colors = $derived($effectiveColors);
  let isIronclad = $derived($currentTheme === "ironclad");

  function zoomIn() {
    zoom.update((z) => z * 1.1);
  }

  function zoomOut() {
    zoom.update((z) => z * 0.9);
  }

  function resetZoom() {
    zoom.set(1);
    panX.set(0);
    panY.set(0);
  }
</script>

<div
  class="absolute bottom-2 left-2 flex items-center gap-1 px-2 py-1 rounded {isIronclad ? 'ironclad-zoom' : 'shadow'}"
  style:background-color={isIronclad ? undefined : colors.FRAME_BG}
  style:color={colors.BUTTON_TEXT}
  style:border={isIronclad ? undefined : `1px solid ${colors.BORDER_COLOR}`}
>
  <button
    class="px-2 py-0.5 text-sm cursor-pointer hover:opacity-70 {isIronclad ? 'ironclad-btn rounded' : ''}"
    onclick={zoomIn}
  >
    +
  </button>
  <button
    class="px-2 py-0.5 text-sm cursor-pointer hover:opacity-70 min-w-[3rem] text-center {isIronclad ? 'ironclad-btn rounded' : ''}"
    onclick={resetZoom}
  >
    {$zoomPercent}%
  </button>
  <button
    class="px-2 py-0.5 text-sm cursor-pointer hover:opacity-70 {isIronclad ? 'ironclad-btn rounded' : ''}"
    onclick={zoomOut}
  >
    &ndash;
  </button>
</div>
