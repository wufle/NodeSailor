<script lang="ts">
  import DialogWrapper from "./DialogWrapper.svelte";
  import { currentTheme, activeDialog } from "../../lib/stores/uiStore";
  import { getThemeColors } from "../../lib/theme/colors";

  let colors = $derived(getThemeColors($currentTheme));

  function close() {
    activeDialog.set(null);
  }
</script>

<DialogWrapper title="Help - Keyboard Shortcuts and Functions" width={550} onClose={close}>
  <div class="text-sm space-y-4" style:color={colors.BUTTON_TEXT}>
    <h2 class="text-base font-bold">Help</h2>

    <div>
      <h3 class="font-bold mb-1">Overview:</h3>
      <p>NodeSailor is a simple network visualization tool. It allows the user to create a network map, display and test their connections with options for pinging, quick launchers for file explorer, web browser, RDP and more with the implementation of custom commands.</p>
    </div>

    <div>
      <h3 class="font-bold mb-1">User Modes:</h3>
      <ul class="list-disc pl-5 space-y-0.5">
        <li><strong>Operator:</strong> Monitor and interact with the network.</li>
        <li><strong>Configuration:</strong> Build and edit the network layout.</li>
      </ul>
    </div>

    <div>
      <h3 class="font-bold mb-1">Operator Mode:</h3>
      <ul class="list-disc pl-5 space-y-0.5">
        <li>Left Click on Node: Ping the node (Green = all IPs connected, Yellow = partial, Red = no connection).</li>
        <li>Right Click on Node: Open context menu.</li>
        <li>Right Click and Drag: Pan the canvas.</li>
        <li>Scroll Wheel: Zoom in and out.</li>
        <li>Who am I?: Highlight node matching active system IP address.</li>
        <li>Ping All: Ping every node.</li>
        <li>Clear Status: Reset node status.</li>
      </ul>
    </div>

    <div>
      <h3 class="font-bold mb-1">Configuration Mode:</h3>
      <ul class="list-disc pl-5 space-y-0.5">
        <li>Double Left Click: Create a new node.</li>
        <li>Shift + Double Left Click: Add a sticky note.</li>
        <li>Middle Click: Create a connection line between two nodes.</li>
        <li>Shift + Middle Click: Remove connection line.</li>
        <li>Left Click + Drag: Move nodes or notes.</li>
        <li>Right Click on Node: Open context menu.</li>
      </ul>
    </div>

    <div>
      <h3 class="font-bold mb-1">Groups:</h3>
      <p>Groups allow the configurator to visually organize nodes into labeled rectangles. Use the Groups button to create, edit, or remove groups.</p>
    </div>

    <div>
      <h3 class="font-bold mb-1">Node List Editor:</h3>
      <p>Presents all nodes in a table for quick editing. Access via the Node List button.</p>
    </div>

    <div>
      <h3 class="font-bold mb-1">Custom Commands:</h3>
      <ul class="list-disc pl-5 space-y-0.5">
        <li>Access through 'Start Menu &gt; Configuration Menu'.</li>
        <li>Use placeholders like &#123;ip&#125;, &#123;name&#125;, &#123;file&#125;, &#123;web&#125;.</li>
        <li>Example: ping &#123;ip&#125; -t</li>
      </ul>
    </div>

    <div>
      <h3 class="font-bold mb-1">Keyboard Shortcuts:</h3>
      <ul class="list-disc pl-5 space-y-0.5">
        <li>Ctrl+Shift+C: Change color theme</li>
        <li>Ctrl+S: Save</li>
        <li>Ctrl+L: Load</li>
        <li>F1: Help</li>
        <li>Arrow keys: Pan canvas</li>
      </ul>
    </div>
  </div>
</DialogWrapper>
