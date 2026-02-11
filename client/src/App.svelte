<script lang="ts">
  import { fade, scale } from "svelte/transition";
  import { quintOut } from "svelte/easing";

  const backendUrl = import.meta.env.VITE_API_URL_FASTAPI;

  let links = $state<any>();
  let newUrl = $state<string>("");
  let newId = $state<string>("");
  let headerRows = $state<Array<{key: string, value: string}>>([{key: "", value: ""}]);
  let editingLinkId = $state<string | null>(null);
  let editUrl = $state<string>("");
  let editHeaderRows = $state<Array<{key: string, value: string}>>([{key: "", value: ""}]);

  function addHeaderRow() {
    headerRows = [...headerRows, {key: "", value: ""}];
  }

  function removeHeaderRow(index: number) {
    if (headerRows.length > 1) {
      headerRows = headerRows.filter((_, i) => i !== index);
    }
  }

  function addEditHeaderRow() {
    editHeaderRows = [...editHeaderRows, {key: "", value: ""}];
  }

  function removeEditHeaderRow(index: number) {
    if (editHeaderRows.length > 1) {
      editHeaderRows = editHeaderRows.filter((_, i) => i !== index);
    }
  }

  function headersToObject(rows: Array<{key: string, value: string}>): Record<string, string> {
    const obj: Record<string, string> = {};
    rows.forEach(row => {
      if (row.key.trim() && row.value.trim()) {
        obj[row.key.trim()] = row.value.trim();
      }
    });
    return obj;
  }

  function objectToHeaders(obj: Record<string, string>): Array<{key: string, value: string}> {
    const entries = Object.entries(obj);
    if (entries.length === 0) {
      return [{key: "", value: ""}];
    }
    return entries.map(([key, value]) => ({key, value}));
  }

  let notification = $state<{type: 'success' | 'error', message: string} | null>(null);

  function showNotification(type: 'success' | 'error', message: string) {
    notification = { type, message };
    setTimeout(() => {
      notification = null;
    }, 3000);
  }

  async function addLink() {
    if (!newUrl.trim()) {
      showNotification('error', 'Please enter a URL');
      return;
    }
    try {
      const headersObj = headersToObject(headerRows);

      const response = await fetch(`${backendUrl}/api/add`, {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({
          id: newId,
          url: newUrl,
          headers: headersObj,
        }),
      });
      if (response.ok) {
        const data = await response.json();
        links = [...links, data.data];
        newUrl = "";
        newId = "";
        headerRows = [{key: "", value: ""}];
        
        // Close dialog
        const dialog = document.getElementById('add-url-dialog');
        if(dialog) dialog.classList.add('hidden');
        
        // Show notification
        showNotification('success', 'URL added successfully!');
      } else {
        showNotification('error', 'Failed to add URL');
      }
    } catch (error) {
      console.error(error);
      showNotification('error', 'An error occurred');
    }
  }

  async function updateLink(id: string) {
    try {
      const headersObj = headersToObject(editHeaderRows);

      const response = await fetch(`${backendUrl}/api/update/${id}`, {
        method: "PUT",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({
          url: editUrl,
          headers: headersObj,
        }),
      });
      if (response.ok) {
        fetchLinks();
        editingLinkId = null;
      }
    } catch (error) {
      console.error(error);
    }
  }

  function startEdit(link: any) {
    editingLinkId = link.id;
    editUrl = link.url;
    editHeaderRows = objectToHeaders(link.headers || {});
  }

  function cancelEdit() {
    editingLinkId = null;
    editUrl = "";
    editHeaderRows = [{key: "", value: ""}];
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
  class="min-h-screen bg-gradient-to-b from-slate-900 to-slate-800 p-4 md:p-8"
  in:fade={{ duration: 300, easing: quintOut }}
>
  <!-- Notification -->
  {#if notification}
    <div
      class="fixed top-4 right-4 px-6 py-3 rounded-lg shadow-lg z-50 transition-all duration-300"
      class:bg-green-500={notification.type === 'success'}
      class:bg-red-500={notification.type === 'error'}
      in:scale={{ duration: 200, easing: quintOut }}
    >
      <span class="text-white font-medium">{notification.message}</span>
    </div>
  {/if}

  <div class="max-w-7xl mx-auto">
    <div class="flex justify-between items-center mb-6">
      <h1
        class="text-3xl md:text-4xl font-bold text-white"
      >
        URL Monitor
      </h1>
      <button
        onclick={() => {
          newUrl = '';
          newId = '';
          headerRows = [{key: '', value: ''}];
          const dialog = document.getElementById('add-url-dialog');
          if(dialog) dialog.classList.remove('hidden');
        }}
        class="px-4 py-2 bg-amber-600 text-white rounded-lg hover:bg-amber-500 transition-colors border border-amber-500"
      >
        Add New URL
      </button>
    </div>

    <div class="bg-slate-800 rounded-lg shadow-lg p-6 border border-slate-700">
      <h2 class="text-xl font-semibold mb-4 text-white">Monitored URLs</h2>
      <div class="space-y-4 max-h-[calc(100vh-200px)] overflow-y-auto pr-2">
        {#each links as link (link?.id)}
          {#if editingLinkId === link.id}
            <div
              class="bg-slate-700 rounded-lg shadow p-4 border border-amber-500"
              in:scale={{ duration: 200, easing: quintOut }}
            >
              <div class="flex flex-col gap-4">
                <h3 class="text-lg font-semibold text-white">
                  Edit Link: {link.id}
                </h3>
                <input
                  type="url"
                  bind:value={editUrl}
                  placeholder="Enter URL"
                  class="px-4 py-2 rounded-lg border border-slate-600 focus:ring-2 focus:ring-amber-500 bg-slate-600 text-white placeholder-slate-400"
                />
                <div>
                  <label class="block text-sm font-medium text-slate-300 mb-2">
                    Custom Headers (Key-Value Pairs)
                  </label>
                  <div class="space-y-2 mb-2">
                    {#each editHeaderRows as row, index (index)}
                      <div class="flex gap-2 items-center">
                        <input
                          type="text"
                          bind:value={row.key}
                          placeholder="Header key"
                          class="flex-1 px-3 py-1.5 rounded border border-slate-600 bg-slate-600 text-white text-sm placeholder-slate-400"
                        />
                        <span class="text-slate-400">:</span>
                        <input
                          type="text"
                          bind:value={row.value}
                          placeholder="Header value"
                          class="flex-1 px-3 py-1.5 rounded border border-slate-600 bg-slate-600 text-white text-sm placeholder-slate-400"
                        />
                        {#if editHeaderRows.length > 1}
                          <button
                            onclick={() => removeEditHeaderRow(index)}
                            class="p-1.5 text-red-400 hover:bg-red-900 rounded"
                            type="button"
                          >
                            Remove
                          </button>
                        {/if}
                      </div>
                    {/each}
                  </div>
                  <button
                    onclick={addEditHeaderRow}
                    class="px-3 py-1.5 text-sm bg-slate-600 text-slate-200 rounded hover:bg-slate-500 transition-colors mb-2 border border-slate-500"
                    type="button"
                  >
                    + Add Header Row
                  </button>
                </div>
                <div class="flex gap-2">
                  <button
                    onclick={() => updateLink(link.id)}
                    class="px-4 py-2 bg-green-600 text-white rounded-lg hover:bg-green-500 transition-colors border border-green-500"
                  >
                    Save
                  </button>
                  <button
                    onclick={cancelEdit}
                    class="px-4 py-2 bg-slate-600 text-white rounded-lg hover:bg-slate-500 transition-colors border border-slate-500"
                  >
                    Cancel
                  </button>
                </div>
              </div>
            </div>
          {:else}
            <div
              class="bg-slate-700 rounded-lg shadow p-4 flex items-center justify-between border border-slate-600"
              in:scale={{ duration: 200, easing: quintOut }}
            >
              <div class="flex-1">
                <div class="flex items-center gap-4 mb-2">
                  <div
                    class="w-3 h-3 rounded-full {link.status
                      ? 'bg-emerald-500'
                      : 'bg-rose-500'}"
                  ></div>
                  <div class="flex flex-col">
                    <span class="text-white font-medium">
                      {link.id}
                    </span>
                    <span class="text-slate-300 text-sm truncate">
                      {link.url}
                    </span>
                    <span class="text-sm text-slate-400">
                      Last checked: {link.last_checked || "Never"}
                    </span>
                  </div>
                </div>
                {#if Object.keys(link.headers || {}).length > 0}
                  <div class="ml-7 mt-2">
                    <span class="text-xs font-medium text-slate-400">
                      Headers:
                    </span>
                    <div class="text-xs text-slate-300 bg-slate-900 p-2 rounded mt-1 overflow-x-auto border border-slate-600">
                      {#each Object.entries(link.headers || {}) as [key, value]}
                        <div class="font-mono">{key}: {value}</div>
                      {/each}
                    </div>
                  </div>
                {/if}
              </div>
              <div class="flex gap-2">
                <button
                  onclick={() => startEdit(link)}
                  class="p-2 text-amber-400 hover:bg-amber-900 rounded-lg transition-colors"
                >
                  Edit
                </button>
                <button
                  onclick={() => deleteLink(link.id)}
                  class="p-2 text-rose-400 hover:bg-rose-900 rounded-lg transition-colors"
                >
                  Delete
                </button>
              </div>
            </div>
          {/if}
        {/each}
      </div>
    </div>

    <!-- Dialog for adding new URL -->
    <div class="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center p-4 z-50 hidden" id="add-url-dialog">
      <div class="bg-slate-800 rounded-lg shadow-xl w-full max-w-md p-6 border border-slate-600">
        <h2 class="text-xl font-semibold mb-4 text-white">Add New URL</h2>
        <div class="flex flex-col gap-4">
          <input
            type="text"
            bind:value={newId}
            placeholder="Enter ID (required)"
            class="px-4 py-2 rounded-lg border border-slate-600 focus:ring-2 focus:ring-amber-500 bg-slate-700 text-white placeholder-slate-400"
          />
          <input
            type="url"
            bind:value={newUrl}
            placeholder="Enter URL to monitor"
            class="px-4 py-2 rounded-lg border border-slate-600 focus:ring-2 focus:ring-amber-500 bg-slate-700 text-white placeholder-slate-400"
          />

          <div>
            <label class="block text-sm font-medium text-slate-300 mb-2">
              Custom Headers (Key-Value Pairs)
            </label>
            <div class="space-y-2 mb-2">
              {#each headerRows as row, index (index)}
                <div class="flex gap-2 items-center">
                  <input
                    type="text"
                    bind:value={row.key}
                    placeholder="Header key (e.g., Authorization)"
                    class="flex-1 px-3 py-1.5 rounded border border-slate-600 bg-slate-700 text-white text-sm placeholder-slate-400"
                  />
                  <span class="text-slate-400">:</span>
                  <input
                    type="text"
                    bind:value={row.value}
                    placeholder="Header value (e.g., Bearer token)"
                    class="flex-1 px-3 py-1.5 rounded border border-slate-600 bg-slate-700 text-white text-sm placeholder-slate-400"
                  />
                  {#if headerRows.length > 1}
                    <button
                      onclick={() => removeHeaderRow(index)}
                      class="p-1.5 text-rose-400 hover:bg-rose-900 rounded"
                      type="button"
                    >
                      Remove
                    </button>
                  {/if}
                </div>
              {/each}
            </div>
            <button
              onclick={addHeaderRow}
              class="px-3 py-1.5 text-sm bg-slate-600 text-slate-200 rounded hover:bg-slate-500 transition-colors mb-4 border border-slate-500"
              type="button"
            >
              + Add Header Row
            </button>
            <p class="text-xs text-slate-400">
              Add custom HTTP headers as key-value pairs
            </p>
          </div>

          <div class="flex gap-2">
            <button
              onclick={addLink}
              class="flex-1 px-4 py-2 bg-amber-600 text-white rounded-lg hover:bg-amber-500 transition-colors border border-amber-500"
            >
              Add URL
            </button>
            <button
              onclick={() => {
                const dialog = document.getElementById('add-url-dialog');
                if(dialog) dialog.style.display='none';
              }}
              class="flex-1 px-4 py-2 bg-slate-600 text-white rounded-lg hover:bg-slate-500 transition-colors border border-slate-500"
            >
              Cancel
            </button>
          </div>
        </div>
      </div>
    </div>

  </div>
</div>
