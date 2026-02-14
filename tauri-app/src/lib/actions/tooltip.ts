import { get } from "svelte/store";
import { isDark, currentTheme } from "../stores/uiStore";


export function tooltip(element: HTMLElement, text: string) {
  let tooltipDiv: HTMLDivElement;
  let timeoutId: number;
  let currentText = text;

  function createTooltip(e: MouseEvent) {
    if (!currentText) return;

    // Clear any existing timeout
    clearTimeout(timeoutId);

    // Set a delay before showing the tooltip
    timeoutId = window.setTimeout(() => {
      tooltipDiv = document.createElement("div");
      tooltipDiv.classList.add("tooltip"); // Apply base tooltip styling
      tooltipDiv.textContent = currentText;

      // Apply theme-specific styling directly
      const dark = get(isDark);
      const theme = get(currentTheme);

      if (dark || theme === "ironclad") {
        // Dark theme colors (from TooltipWrapper.svelte's :global(.dark) .tooltip)
        tooltipDiv.style.backgroundColor = "rgba(30, 30, 30, 0.95)";
        tooltipDiv.style.color = "#ffffff";
        tooltipDiv.style.borderColor = "rgba(255, 255, 255, 0.2)";
      } else {
        // Light theme colors (from TooltipWrapper.svelte's :global(.light) .tooltip)
        tooltipDiv.style.backgroundColor = "rgba(255, 255, 255, 0.95)";
        tooltipDiv.style.color = "#000000";
        tooltipDiv.style.borderColor = "rgba(0, 0, 0, 0.2)";
      }


      document.body.appendChild(tooltipDiv);
      positionTooltip(e);
    }, 500); // 500ms delay
  }

  function removeTooltip() {
    clearTimeout(timeoutId); // Clear timeout if mouse leaves before tooltip is shown
    if (tooltipDiv && document.body.contains(tooltipDiv)) {
      document.body.removeChild(tooltipDiv);
    }
  }

  function positionTooltip(e: MouseEvent) {
    if (!tooltipDiv) return;

    // Get current scroll position
    const scrollX = window.scrollX || document.documentElement.scrollLeft;
    const scrollY = window.scrollY || document.documentElement.scrollTop;

    // Position the tooltip near the cursor, with an offset
    const x = e.clientX + scrollX + 15; // 15px offset to the right
    const y = e.clientY + scrollY + 15; // 15px offset below

    tooltipDiv.style.position = "absolute";
    tooltipDiv.style.left = `${x}px`;
    tooltipDiv.style.top = `${y}px`;
    tooltipDiv.style.zIndex = "10000"; // Ensure it's on top

    // Optional: Adjust position if it goes off-screen (basic check)
    const rect = tooltipDiv.getBoundingClientRect();
    if (rect.right > window.innerWidth) {
      tooltipDiv.style.left = `${e.clientX + scrollX - rect.width - 15}px`;
    }
    if (rect.bottom > window.innerHeight) {
      tooltipDiv.style.top = `${e.clientY + scrollY - rect.height - 15}px`;
    }
  }

  element.addEventListener("mouseenter", createTooltip);
  element.addEventListener("mouseleave", removeTooltip);
  element.addEventListener("mousemove", positionTooltip);

  return {
    update(newText: string) {
      currentText = newText;
      // If tooltip is already visible and text changes, update it
      if (tooltipDiv && document.body.contains(tooltipDiv)) {
        tooltipDiv.textContent = currentText;
      }
    },
    destroy() {
      removeTooltip();
      element.removeEventListener("mouseenter", createTooltip);
      element.removeEventListener("mouseleave", removeTooltip);
      element.removeEventListener("mousemove", positionTooltip);
    },
  };
}
