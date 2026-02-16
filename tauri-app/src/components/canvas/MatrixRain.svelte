<script lang="ts">
  import { onMount, onDestroy } from "svelte";
  import { terminalEntries } from "../../lib/stores/terminalStore";
  import type { TerminalEntry } from "../../lib/stores/terminalStore";

  let canvasEl: HTMLCanvasElement | undefined = $state(undefined);
  let animationId: number = 0;

  const FONT_SIZE = 13;
  const COLUMN_WIDTH = 10;
  const FRAME_DELAY = 1000 / 30;

  // Terminal messages displayed vertically in columns
  let messages: string[] = [];
  const unsubscribe = terminalEntries.subscribe((entries) => {
    messages = entries.flatMap((e: TerminalEntry) => {
      const parts: string[] = [];
      if (e.command) parts.push(e.command);
      if (e.description) parts.push(e.description);
      if (e.result) parts.push(`[${e.result}]`);
      return parts;
    });
  });

  interface Drop {
    y: number;
    msgIndex: number;  // which message this column is displaying
    charIndex: number; // position within that message
    speed: number;
  }

  let drops: Drop[] = [];
  let lastFrameTime = 0;

  function initDrops(width: number) {
    const numColumns = Math.floor(width / COLUMN_WIDTH);
    drops = [];
    for (let i = 0; i < numColumns; i++) {
      drops.push({
        y: Math.random() * -60,
        msgIndex: Math.floor(Math.random() * Math.max(1, messages.length)),
        charIndex: 0,
        speed: 0.3 + Math.random() * 0.7,
      });
    }
  }

  function getChar(drop: Drop): string {
    if (messages.length === 0) {
      // Fallback: random chars when no terminal output yet
      const fallback = "NODESAILOR>_PING...TRACERT...CONNECT...TIMEOUT...OK";
      return fallback[Math.floor(Math.abs(drop.charIndex)) % fallback.length];
    }
    const msg = messages[drop.msgIndex % messages.length];
    return msg[Math.floor(Math.abs(drop.charIndex)) % msg.length];
  }

  function draw(ctx: CanvasRenderingContext2D, width: number, height: number) {
    // Fade trail — slightly faster fade for readability
    ctx.fillStyle = "rgba(0, 0, 0, 0.07)";
    ctx.fillRect(0, 0, width, height);

    ctx.font = `${FONT_SIZE}px 'Consolas', 'Courier New', monospace`;

    for (let i = 0; i < drops.length; i++) {
      const drop = drops[i];
      const x = i * COLUMN_WIDTH;
      const y = drop.y * FONT_SIZE;

      if (y > 0 && y < height) {
        // Bright head character (white-green)
        ctx.fillStyle = "#aaffaa";
        ctx.fillText(getChar(drop), x, y);

        // Trail characters fade from bright to dim green
        for (let t = 1; t < 4; t++) {
          const trailY = y - t * FONT_SIZE;
          if (trailY > 0) {
            const alpha = 0.7 - t * 0.15;
            ctx.fillStyle = `rgba(0, 255, 0, ${alpha})`;
            const trailChar = getChar({ ...drop, charIndex: drop.charIndex - t });
            ctx.fillText(trailChar, x, trailY);
          }
        }
      }

      drop.y += drop.speed;
      drop.charIndex += 1;

      // Reset when off screen — pick a new message
      if (y > height && Math.random() > 0.975) {
        drop.y = Math.random() * -30;
        drop.speed = 0.3 + Math.random() * 0.7;
        drop.charIndex = 0;
        if (messages.length > 0) {
          drop.msgIndex = Math.floor(Math.random() * messages.length);
        }
      }
    }
  }

  function handleResize() {
    if (!canvasEl) return;
    canvasEl.width = canvasEl.offsetWidth;
    canvasEl.height = canvasEl.offsetHeight;
    initDrops(canvasEl.width);
  }

  onMount(() => {
    if (!canvasEl) return;
    canvasEl.width = canvasEl.offsetWidth;
    canvasEl.height = canvasEl.offsetHeight;

    const ctx = canvasEl.getContext("2d");
    if (!ctx) return;

    initDrops(canvasEl.width);

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
