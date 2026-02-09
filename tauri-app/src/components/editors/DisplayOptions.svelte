<script lang="ts">
  import DialogWrapper from "../dialogs/DialogWrapper.svelte";
  import { isDark, activeDialog } from "../../lib/stores/uiStore";
  import { displayOptions } from "../../lib/stores/networkStore";
  import { getThemeColors } from "../../lib/theme/colors";

  let colors = $derived(getThemeColors($isDark));

  function close() {
    activeDialog.set(null);
  }

  function toggle(key: keyof typeof $displayOptions) {
    displayOptions.update((opts) => ({
      ...opts,
      [key]: !opts[key],
    }));
  }

  function setNodeSize(val: number) {
    displayOptions.update((opts) => ({
      ...opts,
      node_size: val,
    }));
  }
</script>

<DialogWrapper
  title="Display Options"
  width={350}
  onClose={close}
>
  <div class="space-y-3">
    <label class="flex items-center gap-2 text-sm" style:color={colors.BUTTON_TEXT}>
      <input
        type="checkbox"
        checked={$displayOptions.show_connections !== false}
        onchange={() => toggle("show_connections")}
      />
      Show Connections
    </label>

    <label class="flex items-center gap-2 text-sm" style:color={colors.BUTTON_TEXT}>
      <input
        type="checkbox"
        checked={$displayOptions.show_connection_labels !== false}
        onchange={() => toggle("show_connection_labels")}
      />
      Show Connection Labels
    </label>

    <label class="flex items-center gap-2 text-sm" style:color={colors.BUTTON_TEXT}>
      <input
        type="checkbox"
        checked={$displayOptions.show_notes !== false}
        onchange={() => toggle("show_notes")}
      />
      Show Sticky Notes
    </label>

    <label class="flex items-center gap-2 text-sm" style:color={colors.BUTTON_TEXT}>
      <input
        type="checkbox"
        checked={$displayOptions.show_groups !== false}
        onchange={() => toggle("show_groups")}
      />
      Show Groups
    </label>

    <div>
      <label class="block text-sm mb-1" style:color={colors.BUTTON_TEXT}>
        Node Size: {$displayOptions.node_size ?? 14}
      </label>
      <input
        type="range"
        min="8"
        max="32"
        value={$displayOptions.node_size ?? 14}
        class="w-full"
        oninput={(e) =>
          setNodeSize(
            parseInt((e.target as HTMLInputElement).value)
          )}
      />
    </div>
  </div>
</DialogWrapper>
