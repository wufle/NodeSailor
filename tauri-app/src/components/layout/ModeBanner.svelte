<script lang="ts">
  import { groupsModeActive, currentTheme, operatorDragAttempted } from "../../lib/stores/uiStore";
  import { effectiveColors } from "../../lib/theme/colors";
  import { matrixMode } from "../../lib/stores/matrixStore";

  let colors = $derived($effectiveColors);
  let isIronclad = $derived($currentTheme === "ironclad");
  let isMatrix = $derived($matrixMode);

  let showDragNotification = $state(false);
  let dismissTimer: ReturnType<typeof setTimeout> | null = null;

  $effect(() => {
    if ($operatorDragAttempted) {
      operatorDragAttempted.set(false);
      showDragNotification = true;
      if (dismissTimer !== null) clearTimeout(dismissTimer);
      dismissTimer = setTimeout(() => {
        showDragNotification = false;
        dismissTimer = null;
      }, 2500);
    }
  });
</script>

{#if $groupsModeActive}
  <div
    class="text-center py-1.5 text-sm font-bold {isIronclad ? 'ironclad-banner' : ''}"
    style:background-color={isIronclad ? undefined : colors.FRAME_BG}
    style:color={isMatrix ? "#00ff00" : (isIronclad ? "#e09240" : "#ff9900")}
  >
    Groups Mode Active: Click and Drag to create a group. Click a group to edit.
  </div>
{:else if showDragNotification}
  <div
    class="text-center py-1.5 text-sm {isIronclad ? 'ironclad-banner' : ''}"
    style:background-color={isIronclad ? undefined : colors.FRAME_BG}
    style:color={isMatrix ? "#00ff00" : (isIronclad ? "#e09240" : colors.INFO_TEXT)}
  >
    Switch to Configuration mode to make changes
  </div>
{/if}
