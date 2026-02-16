<script lang="ts">
  import { onMount, onDestroy } from "svelte";
  import { terminalEntries } from "../../lib/stores/terminalStore";

  let canvasEl: HTMLCanvasElement | undefined = $state(undefined);
  let animationId: number = 0;

  // Fallback characters when no terminal output exists
  const FALLBACK_CHARS =
    "アイウエオカキクケコサシスセソタチツテトナニヌネノハヒフヘホマミムメモヤユヨラリルレロワヲン" +
    "ABCDEFGHIJKLMNOPQRSTUVWXYZ0123456789@#$%^&*";

  const FONT_SIZE = 14;
  const COLUMN_WIDTH = 18;
  const FRAME_DELAY = 1000 / 30; // ~30 FPS

  // Text pool built from terminal entries
  let textPool: string = "";
  const unsubscribe = terminalEntries.subscribe((entries) => {
    if (entries.length === 0) {
      textPool = "";
      return;
    }
    // Concatenate all terminal text into one long string
    textPool = entries
      .map((e) => [e.command, e.description, e.result].filter(Boolean).join(" "))
      .join(" | ");
  });

  interface Drop {
    y: number; // current row position
    textOffset: number; // position within text pool or fallback
    speed: number; // rows per tick (randomized)
  }

  let drops: Drop[] = [];
  let lastFrameTime = 0;

  function initDrops(width: number) {
    const numColumns = Math.floor(width / COLUMN_WIDTH);
    drops = [];
    for (let i = 0; i < numColumns; i++) {
      drops.push({
        y: Math.random() * -50,
        textOffset: Math.floor(Math.random() * 1000),
        speed: 0.5 + Math.random() * 0.8,
      });
    }
  }

  function getChar(drop: Drop): string {
    const source = textPool || FALLBACK_CHARS;
    const idx = Math.floor(Math.abs(drop.textOffset)) % source.length;
    return source[idx];
  }

  function draw(ctx: CanvasRenderingContext2D, width: number, height: number) {
    // Fade trail
    ctx.fillStyle = "rgba(0, 0, 0, 0.06)";
    ctx.fillRect(0, 0, width, height);

    ctx.font = `${FONT_SIZE}px 'Consolas', 'Courier New', monospace`;

    for (let i = 0; i < drops.length; i++) {
      const drop = drops[i];
      const x = i * COLUMN_WIDTH;
      const y = drop.y * FONT_SIZE;

      if (y > 0 && y < height) {
        // Bright head character
        ctx.fillStyle = "#aaffaa";
        ctx.fillText(getChar(drop), x, y);

        // Slightly dimmer trail character one row back
        if (y - FONT_SIZE > 0) {
          ctx.fillStyle = "#00ff00";
          const trailDrop = { ...drop, textOffset: drop.textOffset - 1 };
          ctx.fillText(getChar(trailDrop), x, y - FONT_SIZE);
        }
      }

      drop.y += drop.speed;
      drop.textOffset += 1;

      // Reset when off screen
      if (y > height && Math.random() > 0.975) {
        drop.y = Math.random() * -20;
        drop.speed = 0.5 + Math.random() * 0.8;
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
