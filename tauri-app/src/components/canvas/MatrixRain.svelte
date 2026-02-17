<script lang="ts">
  import { onMount, onDestroy } from "svelte";
  import { terminalEntries } from "../../lib/stores/terminalStore";
  import type { TerminalEntry } from "../../lib/stores/terminalStore";

  let canvasEl: HTMLCanvasElement | undefined = $state(undefined);
  let animationId: number = 0;

  const FONT_SIZE = 14;
  const ROW_HEIGHT = 70;
  const COLUMN_WIDTH = 28;
  const FRAME_DELAY = 1000 / 15;

  // Event-driven drops — spawned by terminal activity
  interface Drop {
    x: number;       // pixel x position
    y: number;        // current row position
    text: string;     // the message this drop displays
    charIndex: number;
    speed: number;
    done: boolean;    // true when fully off-screen
  }

  const TRAIL_LENGTH = 1;

  let activeDrops: Drop[] = [];
  let occupiedColumns: Set<number> = new Set();
  let numColumns = 0;
  let lastFrameTime = 0;
  let lastEntryCount = 0;
  let ambientTimer = 0;

  // Track new terminal entries and spawn drops for them
  const unsubscribe = terminalEntries.subscribe((entries) => {
    if (entries.length <= lastEntryCount) {
      lastEntryCount = entries.length;
      return;
    }

    // Get new entries since last check
    const newEntries = entries.slice(lastEntryCount);
    lastEntryCount = entries.length;

    // Spawn drops for each new entry, staggered slightly
    for (let i = 0; i < newEntries.length; i++) {
      const entry = newEntries[i];
      const parts: string[] = [];
      if (entry.command) parts.push(entry.command);
      if (entry.description) parts.push(entry.description);
      if (entry.result) parts.push(`[${entry.result}]`);
      const text = parts.join(" ");

      // Spawn 1-3 drops per entry in random columns
      const dropCount = 1 + Math.floor(Math.random() * 3);
      for (let d = 0; d < dropCount; d++) {
        setTimeout(() => {
          spawnDrop(text);
        }, i * 80 + d * 40); // stagger: entries 80ms apart, extra drops 40ms apart
      }
    }
  });

  function spawnDrop(text: string) {
    if (numColumns === 0) return;

    // Try to find an unoccupied column (up to 10 attempts)
    let col = -1;
    for (let attempt = 0; attempt < 10; attempt++) {
      const candidate = Math.floor(Math.random() * numColumns);
      if (!occupiedColumns.has(candidate)) {
        col = candidate;
        break;
      }
    }
    if (col === -1) return; // All columns busy, skip this drop

    occupiedColumns.add(col);
    activeDrops.push({
      x: col * COLUMN_WIDTH,
      y: -2 - Math.random() * 5,
      text,
      charIndex: 0,
      speed: 0.12 + Math.random() * 0.18,
      done: false,
    });
  }

  function getChar(drop: Drop, offset: number): string {
    const idx = Math.floor(Math.abs(drop.charIndex - offset)) % drop.text.length;
    return drop.text[idx];
  }

  function draw(ctx: CanvasRenderingContext2D, width: number, height: number) {
    // Fade trail (slow fade for longer-lasting characters)
    ctx.fillStyle = "rgba(0, 0, 0, 0.1)";
    ctx.fillRect(0, 0, width, height);

    ctx.font = `${FONT_SIZE}px 'Consolas', 'Courier New', monospace`;

    // Occasional ambient drop when idle (very sparse)
    ambientTimer++;
    if (ambientTimer > 60) {
      ambientTimer = 0;
      if (Math.random() < 0.4) {
        spawnDrop("NODESAILOR              ");
        spawnDrop("N O D E S A I L O R          ");
      }
    }

    for (const drop of activeDrops) {
      const y = drop.y * ROW_HEIGHT;

      if (y > 0 && y < height) {
        // Bright head character
        ctx.fillStyle = "#aaffaa";
        ctx.fillText(getChar(drop, 0), drop.x, y);

        // Trail chars (longer, smoother fade)
        for (let t = 1; t < TRAIL_LENGTH; t++) {
          const trailY = y - t * ROW_HEIGHT;
          if (trailY > 0) {
            const alpha = 0.6 * (1 - t / TRAIL_LENGTH);
            ctx.fillStyle = `rgba(0, 255, 0, ${alpha})`;
            ctx.fillText(getChar(drop, t), drop.x, trailY);
          }
        }
      }

      drop.y += drop.speed;
      drop.charIndex += 1;

      // Free the column once the head is past 60% of the canvas
      const col = Math.round(drop.x / COLUMN_WIDTH);
      if (y > height * 0.4) {
        occupiedColumns.delete(col);
      }

      // Mark done when trail is fully off screen
      if (y > height + ROW_HEIGHT * TRAIL_LENGTH) {
        drop.done = true;
      }
    }

    // Clean up finished drops
    activeDrops = activeDrops.filter((d) => !d.done);
  }

  function handleResize() {
    if (!canvasEl) return;
    canvasEl.width = canvasEl.offsetWidth;
    canvasEl.height = canvasEl.offsetHeight;
    numColumns = Math.floor(canvasEl.width / COLUMN_WIDTH);
  }

  onMount(() => {
    if (!canvasEl) return;
    canvasEl.width = canvasEl.offsetWidth;
    canvasEl.height = canvasEl.offsetHeight;
    numColumns = Math.floor(canvasEl.width / COLUMN_WIDTH);

    const ctx = canvasEl.getContext("2d");
    if (!ctx) return;

    function animate(timestamp: number) {
      if (timestamp - lastFrameTime >= FRAME_DELAY) {
        lastFrameTime = timestamp;
        draw(ctx!, canvasEl!.width, canvasEl!.height);
      }
      animationId = requestAnimationFrame(animate);
    }

    animationId = requestAnimationFrame(animate);
    window.addEventListener("resize", handleResize);
  });

  onDestroy(() => {
    if (animationId) cancelAnimationFrame(animationId);
    window.removeEventListener("resize", handleResize);
    unsubscribe();
  });
</script>

<canvas
  bind:this={canvasEl}
  style="position:absolute;top:0;left:0;width:100%;height:100%;pointer-events:none;z-index:0;"
></canvas>
