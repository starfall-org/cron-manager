<script lang="ts">
  import { fade, scale } from "svelte/transition";
  import { quintOut } from "svelte/easing";

  const backendUrl = import.meta.env.VITE_API_URL_FASTAPI;

  let links = $state<any>();
  let newUrl = $state<string>("");
  let newId = $state<string>("");

  async function addLink() {
    try {
      const response = await fetch(`${backendUrl}/api/add`, {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({
          id: newId,
          url: newUrl,
        }),
      });
      if (response.ok) {
        const data = await response.json();
        links = [...links, data.data];
        newUrl = "";
        newId = "";
      }
    } catch (error) {
      console.error(error);
    }
  }

  async function deleteLink(id: string) {
    try {
      await fetch(`${backendUrl}/api/delete/${id}`, {
        method: "DELETE",
        headers: { "Content-Type": "application/json" },
      });
      fetchLinks();
    } catch (error) {
      console.error(error);
    }
  }

  async function fetchLinks() {
    try {
      const response = await fetch(`${backendUrl}/api/list`);
      const data = await response.json();
      links = data.data;
    } catch (error) {
      console.error(error);
    }
  }

  $effect(() => {
    fetchLinks();
  });
</script>

<div
  class="min-h-screen bg-gradient-to-b from-gray-50 to-gray-100 dark:from-gray-900 dark:to-gray-800 p-8"
  in:fade={{ duration: 300, easing: quintOut }}
>
  <div class="max-w-4xl mx-auto">
    <h1
      class="text-4xl font-bold text-center mb-8 text-gray-800 dark:text-white"
    >
      URL Monitor
    </h1>

    <div
      class="bg-white dark:bg-gray-800 rounded-lg shadow-lg p-6 mb-8"
      in:scale={{ duration: 300, easing: quintOut }}
    >
      <div class="flex gap-4 flex-col">
        <input
          type="text"
          bind:value={newId}
          placeholder="Enter ID (optional)"
          class="px-4 py-2 rounded-lg border border-gray-300 dark:border-gray-600 focus:ring-2 focus:ring-blue-500 dark:bg-gray-700 dark:text-white"
        />
        <div class="flex gap-4">
          <input
            type="url"
            bind:value={newUrl}
            placeholder="Enter URL to monitor"
            class="flex-1 px-4 py-2 rounded-lg border border-gray-300 dark:border-gray-600 focus:ring-2 focus:ring-blue-500 dark:bg-gray-700 dark:text-white"
          />
          <button
            onclick={addLink}
            class="px-6 py-2 bg-blue-500 text-white rounded-lg hover:bg-blue-600 transition-colors"
          >
            Add URL
          </button>
        </div>
      </div>
    </div>

    <div class="grid gap-4">
      {#each links as link (link?.id)}
        <div
          class="bg-white dark:bg-gray-800 rounded-lg shadow p-4 flex items-center justify-between"
          in:scale={{ duration: 200, easing: quintOut }}
        >
          <div class="flex items-center gap-4">
            <div
              class="w-3 h-3 rounded-full {link.status
                ? 'bg-green-500'
                : 'bg-red-500'}"
            ></div>
            <div class="flex flex-col">
              <span class="text-gray-800 dark:text-gray-200 truncate">
                {link.id}
              </span>
              <span class="text-sm text-gray-500 dark:text-gray-400">
                Last checked: {link.last_checked || "Never"}
              </span>
            </div>
          </div>
          <button
            onclick={() => deleteLink(link.id)}
            class="p-2 text-red-500 hover:bg-red-100 dark:hover:bg-red-900 rounded-lg transition-colors"
          >
            Delete
          </button>
        </div>
      {/each}
    </div>
  </div>
</div>
