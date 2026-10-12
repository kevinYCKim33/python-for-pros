import { LitElement, css, html } from "lit";

const statusLabels = {
  planned: "Planned",
  in_progress: "In Progress",
  blocked: "Blocked",
  done: "Done",
};

const priorityLabels = {
  low: "Low",
  medium: "Medium",
  high: "High",
  urgent: "Urgent",
};

const statusSortOrder = {
  planned: 0,
  in_progress: 1,
  blocked: 2,
  done: 3,
};

const prioritySortOrder = {
  low: 0,
  medium: 1,
  high: 2,
  urgent: 3,
};

async function fetchJson(path, { signal } = {}) {
  const response = await fetch(path, {
    headers: { Accept: "application/json" },
    signal,
  });

  if (!response.ok) {
    throw new Error(`Request failed for ${path}`);
  }

  return response.json();
}

class ReleaseTrackerDashboard extends LitElement {
  static properties = {
    projects: { state: true },
    tasks: { state: true },
    selectedProjectSlug: { state: true },
    statusFilter: { state: true },
    priorityFilter: { state: true },
    overdueOnly: { state: true },
    searchText: { state: true },
    sortColumn: { state: true },
    sortDirection: { state: true },
    loading: { state: true },
    errorMessage: { state: true },
    lastUpdated: { state: true },
  };

  static styles = css`
    :host {
      display: block;
    }

    .layout {
      display: grid;
      gap: 18px;
    }

    .topbar,
    .panel {
      background: var(--surface);
      border: 1px solid var(--border);
      box-shadow: var(--shadow);
      backdrop-filter: blur(16px);
    }

    .topbar {
      padding: 16px 18px;
      border-radius: 22px;
      display: flex;
      align-items: center;
      justify-content: space-between;
      gap: 16px;
    }

    h1,
    h2,
    h3 {
      margin: 0;
      font-family: "Fraunces", Georgia, serif;
      font-weight: 650;
      letter-spacing: -0.03em;
    }

    .app-title {
      display: grid;
      gap: 4px;
    }

    .app-title h1 {
      font-size: 1.2rem;
      line-height: 1.05;
    }

    .app-kicker {
      color: var(--accent);
      font-size: 0.78rem;
      font-weight: 800;
      letter-spacing: 0.08em;
      text-transform: uppercase;
    }

    .meta-row,
    .meta,
    .subtle,
    .project-slug,
    .task-meta,
    .empty-state,
    .error-state {
      color: var(--muted);
    }

    .meta-row {
      font-size: 0.92rem;
    }

    .topbar-actions {
      display: flex;
      flex-wrap: wrap;
      gap: 10px;
    }

    .topbar-actions a,
    .topbar-actions button,
    .filter-toggle,
    .project-button,
    .refresh-button {
      appearance: none;
      border: 0;
      border-radius: 999px;
      font: inherit;
      cursor: pointer;
      transition:
        transform 160ms ease,
        background-color 160ms ease,
        border-color 160ms ease,
        color 160ms ease;
    }

    .topbar-actions a,
    .topbar-actions button,
    .refresh-button {
      display: inline-flex;
      align-items: center;
      justify-content: center;
      min-height: 40px;
      padding: 0 14px;
      text-decoration: none;
      background: var(--surface-strong);
      border: 1px solid var(--border);
      color: var(--text);
    }

    .topbar-actions a:hover,
    .topbar-actions button:hover,
    .filter-toggle:hover,
    .project-button:hover,
    .refresh-button:hover {
      transform: translateY(-1px);
    }


    .workspace {
      display: grid;
      grid-template-columns: 320px minmax(0, 1fr);
      gap: 24px;
      align-items: start;
    }

    .panel {
      border-radius: 28px;
      padding: 22px;
      display: grid;
      gap: 18px;
    }

    .panel-header {
      display: flex;
      align-items: center;
      justify-content: space-between;
      gap: 12px;
    }

    .panel-header p {
      margin: 6px 0 0;
      color: var(--muted);
    }

    .project-list {
      display: grid;
      gap: 10px;
    }

    .project-button {
      width: 100%;
      padding: 16px;
      text-align: left;
      background: var(--surface-strong);
      border: 1px solid transparent;
      display: grid;
      gap: 4px;
    }

    .project-button.active {
      border-color: rgba(23, 107, 109, 0.3);
      background: linear-gradient(180deg, rgba(23, 107, 109, 0.14), rgba(255, 255, 255, 0.88));
    }

    .project-button strong {
      font-size: 1rem;
    }

    .project-slug {
      font-size: 0.88rem;
    }

    .filters {
      display: grid;
      grid-template-columns: 1.3fr repeat(3, minmax(0, 0.8fr));
      gap: 12px;
    }

    .field {
      display: grid;
      gap: 6px;
    }

    .field label {
      font-size: 0.82rem;
      font-weight: 700;
      color: var(--muted);
      text-transform: uppercase;
      letter-spacing: 0.04em;
    }

    .field input,
    .field select {
      min-height: 44px;
      padding: 0 14px;
      border-radius: 14px;
      border: 1px solid var(--border);
      background: rgba(255, 255, 255, 0.9);
      color: var(--text);
      font: inherit;
    }

    .filter-toggle {
      min-height: 44px;
      padding: 0 14px;
      border: 1px solid var(--border);
      background: rgba(255, 255, 255, 0.82);
      color: var(--text);
      align-self: end;
    }

    .filter-toggle.active {
      background: var(--accent);
      color: white;
      border-color: transparent;
    }

    .task-table {
      width: 100%;
      border-collapse: collapse;
    }

    .task-table th,
    .task-table td {
      padding: 14px 12px;
      text-align: left;
      border-bottom: 1px solid rgba(18, 32, 39, 0.08);
      vertical-align: top;
    }

    .task-table th {
      padding-top: 10px;
      padding-bottom: 10px;
    }

    .sort-button {
      display: inline-flex;
      align-items: center;
      gap: 6px;
      padding: 0;
      border: 0;
      background: transparent;
      color: var(--muted);
      font: inherit;
      font-size: 0.82rem;
      font-weight: 700;
      letter-spacing: 0.04em;
      text-transform: uppercase;
      cursor: pointer;
    }

    .sort-button.active {
      color: var(--text);
    }

    .sort-indicator {
      font-size: 0.9rem;
      line-height: 1;
    }

    .task-title {
      display: grid;
      gap: 4px;
    }

    .badge-row {
      display: flex;
      flex-wrap: wrap;
      gap: 8px;
    }

    .badge {
      display: inline-flex;
      align-items: center;
      min-height: 28px;
      padding: 0 10px;
      border-radius: 999px;
      font-size: 0.78rem;
      font-weight: 700;
      letter-spacing: 0.03em;
      text-transform: uppercase;
    }

    .badge.status {
      background: rgba(106, 136, 208, 0.16);
      color: #3452a2;
    }

    .badge.priority {
      background: rgba(111, 120, 128, 0.12);
      color: #4b5563;
    }

    .badge.overdue {
      background: rgba(190, 62, 62, 0.12);
      color: #a83838;
    }

    .badge.status-planned {
      background: rgba(94, 127, 194, 0.15);
      color: #3856a4;
    }

    .badge.status-in_progress {
      background: rgba(210, 144, 36, 0.16);
      color: #9a5b06;
    }

    .badge.status-blocked {
      background: rgba(123, 131, 144, 0.16);
      color: #596271;
    }

    .badge.status-done {
      background: rgba(72, 153, 108, 0.16);
      color: #237347;
    }

    .badge.priority-low {
      background: rgba(128, 138, 150, 0.15);
      color: #55606c;
    }

    .badge.priority-medium {
      background: rgba(99, 132, 210, 0.14);
      color: #3756b2;
    }

    .badge.priority-high {
      background: rgba(222, 141, 54, 0.16);
      color: #a85d0f;
    }

    .badge.priority-urgent {
      background: rgba(163, 63, 115, 0.14);
      color: #9a245d;
    }

    .task-meta {
      font-size: 0.9rem;
    }

    .due-cell {
      display: grid;
      gap: 8px;
    }

    .project-link {
      color: var(--accent);
      font-weight: 700;
      text-decoration: none;
    }

    .project-link:hover {
      text-decoration: underline;
    }

    .empty-state,
    .error-state {
      border-radius: 22px;
      padding: 20px;
      background: rgba(255, 255, 255, 0.6);
      border: 1px dashed rgba(18, 32, 39, 0.12);
    }

    .refresh-button {
      min-height: 40px;
      padding: 0 14px;
    }

    @media (max-width: 1080px) {
      .workspace {
        grid-template-columns: 1fr;
      }
    }

    @media (max-width: 720px) {
      .filters {
        grid-template-columns: 1fr 1fr;
      }

      .task-table,
      .task-table thead,
      .task-table tbody,
      .task-table tr,
      .task-table td {
        display: block;
      }

      .task-table thead {
        display: none;
      }

      .task-table tr {
        padding: 12px 0;
        border-bottom: 1px solid rgba(18, 32, 39, 0.08);
      }

      .task-table td {
        padding: 6px 0;
        border: 0;
      }
    }

    @media (max-width: 560px) {
      .topbar,
      .panel {
        border-radius: 22px;
      }

      .filters {
        grid-template-columns: 1fr;
      }

      .topbar {
        align-items: start;
        flex-direction: column;
      }
    }
  `;

  constructor() {
    super();
    this.projects = [];
    this.tasks = [];
    this.selectedProjectSlug = "";
    this.statusFilter = "";
    this.priorityFilter = "";
    this.overdueOnly = false;
    this.searchText = "";
    this.sortColumn = "due";
    this.sortDirection = "asc";
    this.loading = true;
    this.errorMessage = "";
    this.lastUpdated = "";
    this.tasksRequestController = null;
  }

  connectedCallback() {
    super.connectedCallback();
    const params = new URLSearchParams(window.location.search);
    this.selectedProjectSlug = params.get("project") ?? "";
    this.loadInitialData();
  }

  disconnectedCallback() {
    this.tasksRequestController?.abort();
    super.disconnectedCallback();
  }

  async loadInitialData() {
    this.loading = true;
    this.errorMessage = "";

    try {
      this.projects = await fetchJson("/projects/");
      await this.loadTasks();
    } catch (error) {
      console.error(error);
      this.errorMessage = "The dashboard could not load the API data.";
      this.loading = false;
    }
  }

  async loadTasks() {
    this.tasksRequestController?.abort();
    this.tasksRequestController = new AbortController();

    const params = new URLSearchParams();

    if (this.selectedProjectSlug) {
      params.set("project_slug", this.selectedProjectSlug);
    }

    if (this.statusFilter) {
      params.set("status", this.statusFilter);
    }

    if (this.priorityFilter) {
      params.set("priority", this.priorityFilter);
    }

    if (this.overdueOnly) {
      params.set("overdue_only", "true");
    }

    this.loading = true;
    this.errorMessage = "";

    try {
      const query = params.toString();
      this.tasks = await fetchJson(`/tasks${query ? `?${query}` : ""}`, {
        signal: this.tasksRequestController.signal,
      });
      this.lastUpdated = new Date().toLocaleTimeString([], {
        hour: "numeric",
        minute: "2-digit",
      });
    } catch (error) {
      if (error.name !== "AbortError") {
        console.error(error);
        this.errorMessage = "The task list could not be refreshed.";
      }
    } finally {
      this.loading = false;
    }
  }

  setProject(projectSlug) {
    this.selectedProjectSlug = projectSlug;
    this.syncProjectFilterInUrl();
    this.loadTasks();
  }

  syncProjectFilterInUrl() {
    const url = new URL(window.location.href);

    if (this.selectedProjectSlug) {
      url.searchParams.set("project", this.selectedProjectSlug);
    } else {
      url.searchParams.delete("project");
    }

    window.history.replaceState({}, "", url);
  }

  setStatusFilter(event) {
    this.statusFilter = event.target.value;
    this.loadTasks();
  }

  setPriorityFilter(event) {
    this.priorityFilter = event.target.value;
    this.loadTasks();
  }

  setSearchText(event) {
    this.searchText = event.target.value;
  }

  toggleOverdue() {
    this.overdueOnly = !this.overdueOnly;
    this.loadTasks();
  }

  clearFilters() {
    this.selectedProjectSlug = "";
    this.statusFilter = "";
    this.priorityFilter = "";
    this.overdueOnly = false;
    this.searchText = "";
    this.syncProjectFilterInUrl();
    this.loadTasks();
  }

  isTaskOverdue(task) {
    return Boolean(task.due_date) && task.status !== "done" && new Date(task.due_date) < new Date();
  }

  handleProjectLinkClick(event, projectSlug) {
    event.preventDefault();
    this.setProject(projectSlug);
  }

  get visibleTasks() {
    const needle = this.searchText.trim().toLowerCase();
    const filteredTasks = !needle
      ? [...this.tasks]
      : this.tasks.filter((task) => {
          return [task.title, task.details ?? ""].some((value) =>
            value.toLowerCase().includes(needle)
          );
        });

    return filteredTasks.sort((left, right) => this.compareTasks(left, right));
  }

  compareTasks(left, right) {
    const direction = this.sortDirection === "asc" ? 1 : -1;
    const stringComparer = new Intl.Collator("en", { sensitivity: "base" });
    let comparison = 0;

    if (this.sortColumn === "task") {
      comparison = stringComparer.compare(left.title, right.title);
    } else if (this.sortColumn === "status") {
      comparison = (statusSortOrder[left.status] ?? 99) - (statusSortOrder[right.status] ?? 99);
      if (comparison === 0) {
        comparison = Number(this.isTaskOverdue(left)) - Number(this.isTaskOverdue(right));
      }
    } else if (this.sortColumn === "priority") {
      comparison =
        (prioritySortOrder[left.priority] ?? 99) - (prioritySortOrder[right.priority] ?? 99);
    } else if (this.sortColumn === "due") {
      comparison = this.compareNullableDates(left.due_date, right.due_date);
    } else if (this.sortColumn === "project") {
      comparison = stringComparer.compare(left.project_name, right.project_name);
    }

    if (comparison === 0) {
      comparison = stringComparer.compare(left.title, right.title);
    }

    return comparison * direction;
  }

  compareNullableDates(leftDate, rightDate) {
    if (!leftDate && !rightDate) {
      return 0;
    }

    if (!leftDate) {
      return 1;
    }

    if (!rightDate) {
      return -1;
    }

    return new Date(leftDate).getTime() - new Date(rightDate).getTime();
  }

  toggleSort(column) {
    if (this.sortColumn === column) {
      this.sortDirection = this.sortDirection === "asc" ? "desc" : "asc";
      return;
    }

    this.sortColumn = column;
    this.sortDirection = column === "due" ? "asc" : "asc";
  }

  renderSortHeader(label, column) {
    const isActive = this.sortColumn === column;
    const indicator = !isActive ? "↕" : this.sortDirection === "asc" ? "↑" : "↓";

    return html`
      <button
        class="sort-button ${isActive ? "active" : ""}"
        @click=${() => this.toggleSort(column)}
        type="button"
      >
        <span>${label}</span>
        <span class="sort-indicator" aria-hidden="true">${indicator}</span>
      </button>
    `;
  }

  renderProjectButton(project) {
    const isActive = project.slug === this.selectedProjectSlug;

    return html`
      <button
        class="project-button ${isActive ? "active" : ""}"
        @click=${() => this.setProject(isActive ? "" : project.slug)}
      >
        <strong>${project.name}</strong>
        <span class="project-slug">/${project.slug}</span>
      </button>
    `;
  }

  renderTaskRow(task) {
    return html`
      <tr>
        <td class="task-title">
          <strong>${task.title}</strong>
          <span class="task-meta">${task.details || "No extra implementation notes."}</span>
        </td>
        <td>
          <div class="badge-row">
            <span class="badge status status-${task.status}">
              ${statusLabels[task.status] ?? task.status}
            </span>
            ${this.isTaskOverdue(task) ? html`<span class="badge overdue">Overdue</span>` : ""}
          </div>
        </td>
        <td>
          <span class="badge priority priority-${task.priority}">
            ${priorityLabels[task.priority] ?? task.priority}
          </span>
        </td>
        <td class="due-cell">
          <span>
            ${task.due_date
              ? new Intl.DateTimeFormat("en", { month: "short", day: "numeric" }).format(
                  new Date(task.due_date)
                )
              : "No date"}
          </span>
        </td>
        <td>
          <a
            class="project-link"
            href="/app?project=${task.project_slug}"
            @click=${(event) => this.handleProjectLinkClick(event, task.project_slug)}
          >
            ${task.project_name}
          </a>
        </td>
      </tr>
    `;
  }

  render() {
    return html`
      <div class="layout">
        <section class="topbar">
          <div class="app-title">
            <div class="app-kicker">Release Tracker</div>
            <h1>Project dashboard</h1>
            <div class="meta-row">Last refreshed ${this.lastUpdated || "just now"}</div>
          </div>
          <div class="topbar-actions">
            <a href="/docs" target="_blank" rel="noreferrer">View API docs</a>
            <button class="refresh-button" @click=${() => this.loadInitialData()}>Refresh data</button>
          </div>
        </section>

        <section class="workspace">
          <aside class="panel">
            <div class="panel-header">
              <div>
                <h2>Projects</h2>
                <p>Choose a project to focus the task list.</p>
              </div>
            </div>
            <div class="project-list">
              <button
                class="project-button ${this.selectedProjectSlug === "" ? "active" : ""}"
                @click=${() => this.setProject("")}
              >
                <strong>All projects</strong>
                <span class="project-slug">Entire release board</span>
              </button>
              ${this.projects.map((project) => this.renderProjectButton(project))}
            </div>
          </aside>

          <section class="panel">
            <div class="panel-header">
              <div>
                <h2>Tasks</h2>
                <p>Server-side filters plus a lightweight client-side search.</p>
              </div>
              <button class="refresh-button" @click=${() => this.clearFilters()}>
                Clear filters
              </button>
            </div>

            <div class="filters">
              <div class="field">
                <label for="search">Search</label>
                <input
                  id="search"
                  type="search"
                  .value=${this.searchText}
                  placeholder="Find a task"
                  @input=${this.setSearchText}
                />
              </div>

              <div class="field">
                <label for="status-filter">Status</label>
                <select id="status-filter" .value=${this.statusFilter} @change=${this.setStatusFilter}>
                  <option value="">All</option>
                  <option value="planned">Planned</option>
                  <option value="in_progress">In progress</option>
                  <option value="blocked">Blocked</option>
                  <option value="done">Done</option>
                </select>
              </div>

              <div class="field">
                <label for="priority-filter">Priority</label>
                <select
                  id="priority-filter"
                  .value=${this.priorityFilter}
                  @change=${this.setPriorityFilter}
                >
                  <option value="">All</option>
                  <option value="low">Low</option>
                  <option value="medium">Medium</option>
                  <option value="high">High</option>
                  <option value="urgent">Urgent</option>
                </select>
              </div>

              <button
                class="filter-toggle ${this.overdueOnly ? "active" : ""}"
                @click=${this.toggleOverdue}
              >
                ${this.overdueOnly ? "Showing overdue" : "Overdue only"}
              </button>
            </div>

            ${this.errorMessage
              ? html`<div class="error-state">${this.errorMessage}</div>`
              : this.loading
                ? html`<div class="empty-state">Loading tasks from the API...</div>`
                : this.visibleTasks.length === 0
                  ? html`<div class="empty-state">No tasks match the current filters.</div>`
                  : html`
                      <table class="task-table">
                        <thead>
                          <tr>
                            <th>${this.renderSortHeader("Task", "task")}</th>
                            <th>${this.renderSortHeader("Status", "status")}</th>
                            <th>${this.renderSortHeader("Priority", "priority")}</th>
                            <th>${this.renderSortHeader("Due", "due")}</th>
                            <th>${this.renderSortHeader("Project", "project")}</th>
                          </tr>
                        </thead>
                        <tbody>
                          ${this.visibleTasks.map((task) => this.renderTaskRow(task))}
                        </tbody>
                      </table>
                    `}
          </section>
        </section>
      </div>
    `;
  }
}

customElements.define("release-tracker-dashboard", ReleaseTrackerDashboard);
