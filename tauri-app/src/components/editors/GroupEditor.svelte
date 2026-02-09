<script lang="ts">
  import DialogWrapper from "../dialogs/DialogWrapper.svelte";
  import { currentTheme, isDark, activeDialog } from "../../lib/stores/uiStore";
  import {
    groups,
    updateGroup,
    removeGroup,
    groupColorPresets,
  } from "../../lib/stores/networkStore";
  import { getThemeColors } from "../../lib/theme/colors";

  let colors = $derived(getThemeColors($currentTheme));

  function close() {
    activeDialog.set(null);
  }

  function handleNameChange(index: number, name: string) {
    updateGroup(index, { name });
  }

  function handlePresetChange(index: number, presetId: string) {
    const preset = $groupColorPresets.find(
      (p) => p.id === presetId
    );
    if (preset) {
      updateGroup(index, {
        color_preset_id: presetId,
        light_bg: preset.light_bg,
        light_border: preset.light_border,
        dark_bg: preset.dark_bg,
        dark_border: preset.dark_border,
      });
    }
  }

  function handleDelete(index: number) {
    removeGroup(index);
  }

  let inputClass =
    "w-full px-2 py-1 text-xs rounded border outline-none";
</script>

<DialogWrapper title="Group Editor" width={500} onClose={close}>
  <div class="space-y-4">
    {#each $groups as group, i}
      <div
        class="p-3 rounded"
        style:border="1px solid {colors.BORDER_COLOR}"
        style:background-color={colors.ROW_BG_EVEN}
      >
        <div class="flex items-center gap-2 mb-2">
          <input
            type="text"
            value={group.name}
            class={inputClass}
            style:background-color={colors.ENTRY_FOCUS_BG}
            style:color={colors.ENTRY_TEXT}
            style:border-color={colors.CELL_BORDER}
            onchange={(e) =>
              handleNameChange(
                i,
                (e.target as HTMLInputElement).value
              )}
          />
          <button
            class="text-red-500 hover:text-red-400 text-xs px-2"
            onclick={() => handleDelete(i)}
          >
            Delete
          </button>
        </div>

        <div class="flex flex-wrap gap-2">
          {#each $groupColorPresets as preset}
            <button
              class="px-2 py-1 text-xs rounded border-2"
              style:background-color={$isDark
                ? preset.dark_bg
                : preset.light_bg}
              style:border-color={group.color_preset_id ===
              preset.id
                ? colors.NODE_HIGHLIGHT
                : $isDark
                  ? preset.dark_border
                  : preset.light_border}
              style:color={colors.BUTTON_TEXT}
              onclick={() => handlePresetChange(i, preset.id)}
            >
              {preset.name}
            </button>
          {/each}
        </div>
      </div>
    {/each}

    {#if $groups.length === 0}
      <p class="text-sm opacity-60" style:color={colors.INFO_TEXT}>
        No groups yet. Use Groups mode to draw group rectangles on
        the canvas.
      </p>
    {/if}
  </div>
</DialogWrapper>
