<script lang="ts">
  import DialogWrapper from "../dialogs/DialogWrapper.svelte";
  import { currentTheme, activeDialog } from "../../lib/stores/uiStore";
  import { displayOptions } from "../../lib/stores/networkStore";
  import { effectiveColors } from "../../lib/theme/colors";

  let colors = $derived($effectiveColors);

  function close() {
    activeDialog.set(null);
  }

  // Use local state that syncs with store for proper reactivity
  let showConnections = $state($displayOptions.show_connections !== false);
  let showConnectionLabels = $state($displayOptions.show_connection_labels !== false);
  let showNotes = $state($displayOptions.show_notes !== false);
  let showGroups = $state($displayOptions.show_groups !== false);

  // Update store when local state changes
  $effect(() => {
    displayOptions.update((opts) => ({
      ...opts,
      show_connections: showConnections,
      show_connection_labels: showConnectionLabels,
      show_notes: showNotes,
      show_groups: showGroups,
    }));
  });

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
        bind:checked={showConnections}
      />
      Show Connections
    </label>

    <label class="flex items-center gap-2 text-sm" style:color={colors.BUTTON_TEXT}>
      <input
        type="checkbox"
        bind:checked={showConnectionLabels}
      />
      Show Connection Labels
    </label>

    <label class="flex items-center gap-2 text-sm" style:color={colors.BUTTON_TEXT}>
      <input
        type="checkbox"
        bind:checked={showNotes}
      />
      Show Sticky Notes
    </label>

    <label class="flex items-center gap-2 text-sm" style:color={colors.BUTTON_TEXT}>
      <input
        type="checkbox"
        bind:checked={showGroups}
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
