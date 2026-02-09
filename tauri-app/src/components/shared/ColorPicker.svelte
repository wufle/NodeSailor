<script lang="ts">
  let {
    value = "#000000",
    onchange,
  }: {
    value: string;
    onchange: (color: string) => void;
  } = $props();
</script>

<input
  type="color"
  {value}
  class="w-8 h-8 cursor-pointer border-0 p-0"
  oninput={(e) =>
    onchange((e.target as HTMLInputElement).value)}
/>
