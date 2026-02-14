<script lang="ts">
  import DialogWrapper from "../dialogs/DialogWrapper.svelte";
  import { currentTheme, activeDialog } from "../../lib/stores/uiStore";
  import {
    customCommands,
    nodes,
  } from "../../lib/stores/networkStore";
  import { effectiveColors } from "../../lib/theme/colors";
  import type { CustomCommand } from "../../lib/types/network";

  let colors = $derived($effectiveColors);
  let isIronclad = $derived($currentTheme === "ironclad");

  let selectedCommand = $state<string | null>(null);
  let editName = $state("");
  let editTemplate = $state("");
  let editApplicableAll = $state(true);
  let editApplicableNodes = $state<string[]>([]);
  let saveMessage = $state<string>("");
  let saveMessageTimeout: number | undefined;

  function close() {
    activeDialog.set(null);
  }

  function selectCommand(name: string) {
    selectedCommand = name;
    const cmd = $customCommands[name];
    editName = name;
    if (typeof cmd === "string") {
      editTemplate = cmd;
      editApplicableAll = true;
      editApplicableNodes = [];
    } else {
      editTemplate = (cmd as CustomCommand).template;
      const an = (cmd as CustomCommand).applicable_nodes;
      editApplicableAll = an === null;
      editApplicableNodes = an ?? [];
    }
  }

  function addCommand() {
    const name = "New Command";
    customCommands.update((cmds) => ({
      ...cmds,
      [name]: { template: "", applicable_nodes: null },
    }));
    selectCommand(name);
  }

  function saveCommand() {
    if (!selectedCommand || !editName) return;

    customCommands.update((cmds) => {
      const copy = { ...cmds };
      // Remove old key if renamed
      if (selectedCommand !== editName) {
        delete copy[selectedCommand!];
      }
      copy[editName] = {
        template: editTemplate,
        applicable_nodes: editApplicableAll
          ? null
          : editApplicableNodes,
      };
      return copy;
    });
    selectedCommand = editName;

    // Show save confirmation
    saveMessage = "✓ Saved";
    if (saveMessageTimeout) clearTimeout(saveMessageTimeout);
    saveMessageTimeout = window.setTimeout(() => {
      saveMessage = "";
    }, 2000);
  }

  function deleteCommand() {
    if (!selectedCommand) return;
    customCommands.update((cmds) => {
      const copy = { ...cmds };
      delete copy[selectedCommand!];
      return copy;
    });
    selectedCommand = null;
  }

  function toggleNode(nodeName: string) {
    if (editApplicableNodes.includes(nodeName)) {
      editApplicableNodes = editApplicableNodes.filter(
        (n) => n !== nodeName
      );
    } else {
      editApplicableNodes = [...editApplicableNodes, nodeName];
    }
  }

  let inputClass =
    "w-full px-2 py-1 text-xs rounded border outline-none";
</script>

<DialogWrapper
  title="Custom Commands"
  width={600}
  onClose={close}
>
  <div class="flex gap-4">
    <!-- Command list -->
    <div class="w-1/3 space-y-1">
      {#each Object.keys($customCommands) as name}
        <button
          class="w-full text-left px-2 py-1 text-xs rounded {isIronclad ? 'ironclad-btn' : ''}"
          style:background-color={isIronclad ? undefined : (selectedCommand === name
            ? colors.BUTTON_ACTIVE_BG
            : colors.BUTTON_BG)}
          style:color={colors.BUTTON_TEXT}
          style:border-color={selectedCommand === name && isIronclad ? "#e09240" : undefined}
          onclick={() => selectCommand(name)}
        >
          {name}
        </button>
      {/each}
      <button
        class="w-full text-left px-2 py-1 text-xs rounded mt-2 {isIronclad ? 'ironclad-btn' : ''}"
        style:background-color={isIronclad ? undefined : colors.BUTTON_BG}
        style:color={colors.BUTTON_TEXT}
        onclick={addCommand}
      >
        + Add Command
      </button>
    </div>

    <!-- Editor -->
    <div class="flex-1">
      {#if selectedCommand}
        <div class="space-y-3">
          <div>
            <label
              class="block text-xs mb-1"
              style:color={colors.BUTTON_TEXT}>Name:</label
            >
            <input
              type="text"
              bind:value={editName}
              class={inputClass}
              style:background-color={colors.ENTRY_FOCUS_BG}
              style:color={colors.ENTRY_TEXT}
              style:border-color={colors.CELL_BORDER}
            />
          </div>

          <div>
            <label
              class="block text-xs mb-1"
              style:color={colors.BUTTON_TEXT}
              >Template:</label
            >
            <textarea
              bind:value={editTemplate}
              class="{inputClass} h-20 resize-y"
              style:background-color={colors.ENTRY_FOCUS_BG}
              style:color={colors.ENTRY_TEXT}
              style:border-color={colors.CELL_BORDER}
            ></textarea>
            <p
              class="text-xs opacity-50 mt-1"
              style:color={colors.INFO_TEXT}
            >
              Available: &#123;ip&#125;, &#123;name&#125;, &#123;file&#125;, &#123;web&#125;, &#123;rdp&#125;, &#123;vlan_N&#125;
            </p>
          </div>

          <div>
            <label class="flex items-center gap-2 text-xs" style:color={colors.BUTTON_TEXT}>
              <input
                type="checkbox"
                bind:checked={editApplicableAll}
              />
              Apply to all nodes
            </label>
          </div>

          {#if !editApplicableAll}
            <div
              class="max-h-32 overflow-auto p-2 rounded"
              style:background-color={colors.ROW_BG_EVEN}
              style:border="1px solid {colors.CELL_BORDER}"
            >
              {#each $nodes as node}
                <label
                  class="flex items-center gap-2 text-xs"
                  style:color={colors.BUTTON_TEXT}
                >
                  <input
                    type="checkbox"
                    checked={editApplicableNodes.includes(
                      node.name
                    )}
                    onchange={() => toggleNode(node.name)}
                  />
                  {node.name}
                </label>
              {/each}
            </div>
          {/if}

          <div class="flex gap-2 items-center">
            <button
              class="px-3 py-1.5 text-xs rounded {isIronclad ? 'ironclad-btn' : ''}"
              style:background-color={isIronclad ? undefined : colors.BUTTON_BG}
              style:color={colors.BUTTON_TEXT}
              onclick={saveCommand}
            >
              Save
            </button>
            <button
              class="px-3 py-1.5 text-xs rounded text-red-500 {isIronclad ? 'ironclad-btn' : ''}"
              style:background-color={isIronclad ? undefined : colors.BUTTON_BG}
              onclick={deleteCommand}
            >
              Delete
            </button>
            {#if saveMessage}
              <span
                class="text-xs text-green-500 font-medium"
                style:color={isIronclad ? "#2ecc71" : undefined}
              >
                {saveMessage}
              </span>
            {/if}
          </div>
        </div>
      {:else}
        <p
          class="text-xs opacity-60"
          style:color={colors.INFO_TEXT}
        >
          Select a command to edit or add a new one.
        </p>
      {/if}
    </div>
  </div>
</DialogWrapper>
