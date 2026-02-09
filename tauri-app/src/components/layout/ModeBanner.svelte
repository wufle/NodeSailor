<script lang="ts">
  import { groupsModeActive, currentTheme } from "../../lib/stores/uiStore";
  import { getThemeColors } from "../../lib/theme/colors";

  let colors = $derived(getThemeColors($currentTheme));
</script>

{#if $groupsModeActive}
  <div
    class="text-center py-1 text-sm font-bold"
    style:background-color={colors.FRAME_BG}
    style:color="#ff9900"
  >
    Groups Mode Active: Click and Drag to create a group. Click a group to edit.
  </div>
{/if}
