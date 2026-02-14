<script lang="ts">
  import { groupsModeActive, currentTheme } from "../../lib/stores/uiStore";
  import { effectiveColors } from "../../lib/theme/colors";

  let colors = $derived($effectiveColors);
  let isIronclad = $derived($currentTheme === "ironclad");
</script>

{#if $groupsModeActive}
  <div
    class="text-center py-1.5 text-sm font-bold {isIronclad ? 'ironclad-banner' : ''}"
    style:background-color={isIronclad ? undefined : colors.FRAME_BG}
    style:color={isIronclad ? "#e09240" : "#ff9900"}
  >
    Groups Mode Active: Click and Drag to create a group. Click a group to edit.
  </div>
{/if}
