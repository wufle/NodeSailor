<script lang="ts">
  import DialogWrapper from "./DialogWrapper.svelte";
  import { currentTheme, activeDialog } from "../../lib/stores/uiStore";
  import { effectiveColors } from "../../lib/theme/colors";

  let colors = $derived($effectiveColors);

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
      <h3 class="font-bold mb-1">Navigation (All Modes):</h3>
      <ul class="list-disc pl-5 space-y-0.5">
        <li>Left Click + Drag on empty canvas: Pan the canvas.</li>
        <li>Middle Click + Drag: Pan the canvas (alternative).</li>
        <li>Scroll Wheel: Zoom in and out.</li>
        <li>Arrow Keys: Pan canvas in small increments.</li>
      </ul>
    </div>

    <div>
      <h3 class="font-bold mb-1">Operator Mode:</h3>
      <ul class="list-disc pl-5 space-y-0.5">
        <li>Left Click on Node: Ping the node (Green = all IPs connected, Yellow = partial, Red = no connection).</li>
        <li>Right Click on Node: Open context menu.</li>
        <li>Who am I?: Highlight node matching active system IP address.</li>
        <li>Ping All: Ping every node.</li>
        <li>Clear Status: Reset node status.</li>
      </ul>
    </div>

    <div>
      <h3 class="font-bold mb-1">Configuration Mode:</h3>
      <p class="mb-1">Use the side toolbar or keyboard shortcuts to switch tools:</p>
      <ul class="list-disc pl-5 space-y-0.5">
        <li><strong>Select/Move (V):</strong> Left Click + Drag to move nodes or notes. Default tool.</li>
        <li><strong>Add Node (N):</strong> Click on canvas to create a node. Also: Double-click on empty canvas.</li>
        <li><strong>Connect (C):</strong> Click first node, then click second node to create a connection.</li>
        <li><strong>Add Note (T):</strong> Click on canvas to add a sticky note. Also: Shift + Double-click.</li>
        <li><strong>Escape:</strong> Cancel current operation and return to Select tool.</li>
        <li><strong>Delete:</strong> Delete selected node.</li>
        <li>Right Click on Node: Open context menu (edit, delete, RDP, etc.).</li>
        <li>Right Click on Connection: Edit or delete connection.</li>
        <li>Double-click on Connection Line: Add a waypoint.</li>
      </ul>
    </div>

    <div>
      <h3 class="font-bold mb-1">Groups:</h3>
      <p>Groups allow the configurator to visually organize nodes into labeled rectangles. Use the Groups button to activate group drawing mode, then click and drag on the canvas to draw rectangles.</p>
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
        <li>V: Select/Move tool</li>
        <li>N: Add Node tool</li>
        <li>C: Connect tool</li>
        <li>T: Add Note tool</li>
        <li>Escape: Cancel / Select tool</li>
        <li>Delete: Delete selected element</li>
        <li>Ctrl+S: Save</li>
        <li>Ctrl+L: Load</li>
        <li>Ctrl+Shift+C: Change color theme</li>
        <li>F1: Help</li>
        <li>Arrow keys: Pan canvas</li>
      </ul>
    </div>
  </div>
</DialogWrapper>
