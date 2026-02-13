<script lang="ts">
  import DialogWrapper from "./DialogWrapper.svelte";
  import { currentTheme, activeDialog } from "../../lib/stores/uiStore";
  import { settings } from "../../lib/stores/settingsStore";
  import { getThemeColors } from "../../lib/theme/colors";
  import { invoke } from "@tauri-apps/api/core";

  interface TutorialStep {
    title: string;
    imagePath: string;
    description: string;
    points: string[];
  }

  const tutorialSteps: TutorialStep[] = [
    {
      title: "Creating Your First Node",
      imagePath: "/screenshots/configuration_guidance/c1_new_node.png",
      description: "In Configuration mode, double-click anywhere on the canvas to create a new node.",
      points: [
        "Double-click an empty area to open the node editor",
        "Enter a name for your node",
        "Add IP addresses for different VLANs",
        "Optionally add Remote Desktop, file path, or web URL"
      ]
    },
    {
      title: "Creating Connections",
      imagePath: "/screenshots/configuration_guidance/c2_new_connection.png",
      description: "Connect nodes together to visualize your network topology.",
      points: [
        "Middle-click on the first node",
        "Middle-click on the second node to create a connection",
        "Shift + Middle-click to remove connections",
        "Right-click connections to edit labels"
      ]
    },
    {
      title: "List Editor",
      imagePath: "/screenshots/configuration_guidance/c3_list_editor.png",
      description: "Edit multiple nodes at once using the Node List editor.",
      points: [
        "Access via 'Node List' button in Configuration mode",
        "View all nodes in a table format",
        "Quickly edit node properties",
        "Sort columns by clicking headers"
      ]
    },
    {
      title: "Working with Groups",
      imagePath: "/screenshots/configuration_guidance/c4_groups.png",
      description: "Organize your network visually using groups.",
      points: [
        "Click 'Groups' button to activate group mode",
        "Click and drag to draw group rectangles",
        "Groups can contain multiple nodes",
        "Customize group colors and labels"
      ]
    },
    {
      title: "Custom Commands",
      imagePath: "/screenshots/configuration_guidance/c5_custom_commands.png",
      description: "Create custom commands for quick access to common tasks.",
      points: [
        "Access via Start Menu > 'Custom Commands'",
        "Use placeholders: {ip}, {name}, {file}, {web}",
        "Example: ping {ip} -t",
        "Commands appear in node context menus"
      ]
    },
    {
      title: "Node Pinging",
      imagePath: "/screenshots/operator_guidance/o1_nodeping.png",
      description: "Test connectivity by pinging nodes in Operator mode.",
      points: [
        "Click a node to ping all its IP addresses",
        "Green = all IPs connected",
        "Yellow = partial connectivity",
        "Red = no connection",
        "Use 'Ping All' to test all nodes at once"
      ]
    },
    {
      title: "Context Menu",
      imagePath: "/screenshots/operator_guidance/o2_context_menu.png",
      description: "Right-click nodes to access quick actions.",
      points: [
        "Launch Remote Desktop connections",
        "Open file paths in Explorer",
        "Navigate to web interfaces",
        "Run custom commands"
      ]
    },
    {
      title: "Navigation Controls",
      imagePath: "/screenshots/operator_guidance/o4_navigation_guidance.png",
      description: "Navigate the canvas efficiently.",
      points: [
        "Right-click and drag to pan the canvas",
        "Mouse wheel to zoom in and out",
        "Arrow keys for precise panning"
      ]
    }
  ];

  let currentStep = $state(0);
  let colors = $derived(getThemeColors($currentTheme));
  let isIronclad = $derived($currentTheme === "ironclad");


  async function markTutorialCompleted() {
    const updatedSettings = { ...$settings, tutorial_completed: true };
    await invoke("save_settings", { settings: updatedSettings });
    settings.set(updatedSettings);
  }

  async function close(completed: boolean = false) {
    if (completed || currentStep === tutorialSteps.length - 1) {
      await markTutorialCompleted();
    }
    activeDialog.set(null);
  }

  async function nextStep() {
    if (currentStep < tutorialSteps.length - 1) {
      currentStep++;
    } else {
      await close(true);
    }
  }

  function previousStep() {
    if (currentStep > 0) {
      currentStep--;
    }
  }

  let buttonClass = $derived(
    "px-4 py-2 text-sm rounded hover:opacity-80 transition-opacity" +
    (isIronclad ? " ironclad-btn" : "")
  );
</script>

<DialogWrapper title="Tutorial Walkthrough" width={750} onClose={close}>
  <div class="space-y-4">
    <!-- Progress indicator -->
    <div class="text-center text-sm opacity-60" style:color={colors.BUTTON_TEXT}>
      Step {currentStep + 1} of {tutorialSteps.length}
    </div>

    <!-- Progress bar -->
    <div class="w-full h-1 rounded-full overflow-hidden" style:background-color={colors.CELL_BORDER}>
      <div
        class="h-full transition-all duration-300"
        style:width="{((currentStep + 1) / tutorialSteps.length) * 100}%"
        style:background-color={colors.NODE_HIGHLIGHT}
      ></div>
    </div>

    <!-- Image -->
    <div class="flex justify-center items-center" style:height="384px">
      <img
        src={tutorialSteps[currentStep].imagePath}
        alt={tutorialSteps[currentStep].title}
        class="max-w-full max-h-full object-contain rounded"
        style:border="1px solid {colors.BORDER_COLOR}"
      />
    </div>

    <!-- Content -->
    <div class="space-y-2">
      <h3 class="text-lg font-bold" style:color={colors.BUTTON_TEXT}>
        {tutorialSteps[currentStep].title}
      </h3>

      <p class="text-sm" style:color={colors.BUTTON_TEXT}>
        {tutorialSteps[currentStep].description}
      </p>

      <ul class="list-disc pl-5 space-y-1 text-sm" style:color={colors.BUTTON_TEXT}>
        {#each tutorialSteps[currentStep].points as point}
          <li>{point}</li>
        {/each}
      </ul>
    </div>

    <!-- Navigation buttons -->
    <div class="flex justify-between items-center gap-2 pt-2">
      <button
        class={buttonClass}
        style:background-color={colors.BUTTON_BG}
        style:color={colors.BUTTON_TEXT}
        style:opacity={currentStep === 0 ? "0.5" : "1"}
        disabled={currentStep === 0}
        onclick={previousStep}
      >
        Previous
      </button>

      <button
        class="{buttonClass} px-6"
        style:background-color={colors.BUTTON_BG}
        style:color={colors.BUTTON_TEXT}
        onclick={() => close(false)}
      >
        Skip Tutorial
      </button>

      <button
        class={buttonClass}
        style:background-color={colors.BUTTON_ACTIVE_BG}
        style:color={colors.BUTTON_ACTIVE_TEXT}
        onclick={nextStep}
      >
        {currentStep === tutorialSteps.length - 1 ? "Finish" : "Next"}
      </button>
    </div>
  </div>
</DialogWrapper>
