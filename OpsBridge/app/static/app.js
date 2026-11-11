const $ = (selector) => document.querySelector(selector);
const labels = {
  status: {new:"Novo",in_progress:"Em curso",waiting:"Em espera",resolved:"Resolvido",closed:"Fechado",cancelled:"Cancelado"},
  priority: {low:"Baixa",medium:"Média",high:"Alta",critical:"Crítica"},
  category: {hardware:"Hardware",software:"Software",network:"Rede",access:"Acessos"},
  field: {created:"Criação",title:"Título",description:"Descrição",category:"Categoria",priority:"Prioridade",status:"Estado",assigned_to:"Técnico"},
};
let currentTicket = null;
let searchTimer;
let toastTimer;
const modal = $("#ticketModal");
const form = $("#ticketForm");
const f = (name) => form.elements.namedItem(name);

function escapeHtml(text) {
  return String(text ?? "").replace(/[&<>"']/g, (c) => ({'&':'&amp;','<':'&lt;','>':'&gt;','"':'&quot;',"'":'&#39;'}[c]));
}
function fmtDate(text) {
  if (!text) return "—";
  // SQLite datetime has no timezone; display without incorrectly assuming UTC.
  const d = String(text).replace("T", " ");
  return d.slice(0, 16).replace(/^([0-9]{4})-([0-9]{2})-([0-9]{2})/, "$3/$2/$1");
}
function notify(text, isError = false) {
  const toast = $("#toast");
  toast.textContent = text;
  toast.style.background = isError ? "#a82943" : "#1b2944";
  toast.classList.add("show");
  clearTimeout(toastTimer);
  toastTimer = setTimeout(() => toast.classList.remove("show"), 3500);
}
async function api(path, options = {}) {
  let response;
  try {
    response = await fetch(path, {headers: {"Content-Type":"application/json"}, ...options});
  } catch (error) {
    throw new Error("Não foi possível contactar o servidor. Verifica se o Uvicorn está ativo.");
  }
  const content = await response.json().catch(() => ({}));
  if (!response.ok) {
    const error = content.detail;
    const reason = typeof error === "string" ? error : Array.isArray(error) ? error.map(item => item.msg).join("; ") : `HTTP ${response.status}`;
    throw new Error(reason);
  }
  return content;
}
function getQuery() {
  const params = new URLSearchParams();
  for (const [element, key] of [["#search", "q"],["#statusFilter", "status"],["#priorityFilter", "priority"],["#categoryFilter", "category"]]) {
    const value = $(element).value.trim();
    if (value) params.set(key, value);
  }
  return params.toString();
}
async function refresh() {
  try {
    const [stats, tickets] = await Promise.all([api("/tickets/stats"), api(`/tickets?${getQuery()}`)]);
    $("#statTotal").textContent = stats.total;
    $("#statOpen").textContent = stats.open;
    $("#statCritical").textContent = stats.critical;
    $("#statResolved").textContent = stats.resolved;
    renderRows(tickets);
    $("#ticketCount").textContent = `${tickets.length} ticket(s) apresentados`;
  } catch (error) {
    $("#ticketRows").innerHTML = `<tr><td colspan="7" class="empty">${escapeHtml(error.message)}</td></tr>`;
    notify(error.message, true);
  }
}
function renderRows(tickets) {
  if (!tickets.length) {
    $("#ticketRows").innerHTML = `<tr><td colspan="7" class="empty">Nenhum ticket encontrado. Cria o primeiro pedido ou altera os filtros.</td></tr>`;
    return;
  }
  $("#ticketRows").innerHTML = tickets.map(ticket => `
    <tr>
      <td><span class="ticket-title">${escapeHtml(ticket.title)}</span><span class="ticket-id">#${ticket.id} · ${escapeHtml(ticket.requester)}</span></td>
      <td><span class="tag-category">${labels.category[ticket.category] || escapeHtml(ticket.category)}</span></td>
      <td><span class="pill ${ticket.priority}">${labels.priority[ticket.priority] || escapeHtml(ticket.priority)}</span></td>
      <td><span class="pill ${ticket.status}">${labels.status[ticket.status] || escapeHtml(ticket.status)}</span></td>
      <td>${escapeHtml(ticket.assigned_to || "Não atribuído")}</td>
      <td>${fmtDate(ticket.created_at)}</td>
      <td><button class="view-btn" data-id="${ticket.id}">Detalhes</button></td>
    </tr>`).join("");
}
function setEditMode(isEditing) {
  $("#editFields").hidden = !isEditing;
  $("#requesterField").hidden = isEditing;
  $("#cancelTicket").hidden = !isEditing;
  $("#modalEyebrow").textContent = isEditing ? `TICKET #${currentTicket.id}` : "NOVO PEDIDO";
  $("#modalTitle").textContent = isEditing ? "Detalhes do ticket" : "Criar ticket";
  $("#saveTicket").textContent = isEditing ? "Guardar alterações" : "Criar ticket";
  $("#formError").hidden = true;
}
function openCreate() {
  currentTicket = null;
  form.reset();
  setEditMode(false);
  for (const el of form.querySelectorAll("input, select, textarea")) el.disabled = false;
  $("#saveTicket").disabled = false;
  modal.showModal();
}
async function openEdit(id) {
  try {
    currentTicket = await api(`/tickets/${id}`);
    setEditMode(true);
    for (const key of ["title","description","category","priority","requester","status","assigned_to"]) f(key).value = currentTicket[key] ?? "";
    const locked = ["closed", "cancelled"].includes(currentTicket.status);
    for (const el of form.querySelectorAll("input,select,textarea")) el.disabled = locked;
    $("#saveTicket").disabled = locked;
    $("#cancelTicket").hidden = locked;
    modal.showModal();
    const history = await api(`/tickets/${id}/history`);
    $("#historyList").innerHTML = history.length ? history.map(item =>
      `<div class="history-item"><b>${labels.field[item.field] || escapeHtml(item.field)}</b>: ${escapeHtml(item.old_value || "—")} → ${escapeHtml(item.new_value || "—")}<small>${fmtDate(item.changed_at)}</small></div>`
    ).join("") : "Sem alterações registadas";
  } catch (error) {
    notify(error.message, true);
  }
}
function close() { modal.close(); currentTicket = null; }
async function save(event) {
  event.preventDefault();
  $("#formError").hidden = true;
  if (!form.reportValidity()) return;
  const editing = Boolean(currentTicket);
  const data = editing ? {
    title:f("title").value.trim(),description:f("description").value.trim(),category:f("category").value,
    priority:f("priority").value,status:f("status").value,assigned_to:f("assigned_to").value.trim() || null,
  } : {
    title:f("title").value.trim(),description:f("description").value.trim(),category:f("category").value,
    priority:f("priority").value,requester:f("requester").value.trim(),
  };
  try {
    const path = editing ? `/tickets/${currentTicket.id}` : "/tickets";
    await api(path,{method:editing ? "PUT":"POST",body:JSON.stringify(data)});
    close();
    await refresh();
    notify(editing ? "Ticket atualizado com sucesso." : "Ticket criado com sucesso.");
  } catch(error) {
    $("#formError").textContent = error.message;
    $("#formError").hidden = false;
  }
}
async function cancelTicket() {
  if (!currentTicket || !confirm(`Cancelar o ticket #${currentTicket.id}? O registo permanece no histórico.`)) return;
  try {
    await api(`/tickets/${currentTicket.id}`, {method:"DELETE"});
    close();
    await refresh();
    notify("Ticket cancelado.");
  } catch (error) { notify(error.message,true); }
}
$("#today").textContent = new Intl.DateTimeFormat("pt-PT",{day:"numeric",month:"long",year:"numeric"}).format(new Date());
$("#newTicket").addEventListener("click",openCreate);
$("#refreshButton").addEventListener("click",refresh);
$("#closeModal").addEventListener("click",close);
$("#cancelModal").addEventListener("click",close);
$("#cancelTicket").addEventListener("click",cancelTicket);
form.addEventListener("submit",save);
$("#ticketRows").addEventListener("click",(event) => {
  const button = event.target.closest("button[data-id]");
  if (button) openEdit(Number(button.dataset.id));
});
for (const selector of ["#statusFilter", "#priorityFilter", "#categoryFilter"]) $(selector).addEventListener("change",refresh);
$("#search").addEventListener("input", () => { clearTimeout(searchTimer); searchTimer = setTimeout(refresh, 250); });
refresh();
