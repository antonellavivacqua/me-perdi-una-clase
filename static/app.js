"use strict";

const filters = document.querySelector("#filters");
const course = document.querySelector("#course");
const date = document.querySelector("#date");
const clearDate = document.querySelector("#clear-date");
const feedback = document.querySelector("#feedback");
const classList = document.querySelector("#classes");
const requestList = document.querySelector("#requests");
const count = document.querySelector("#count");
const editor = document.querySelector("#editor");
const form = document.querySelector("#entry-form");
const entryError = document.querySelector("#entry-error");
const saveEntry = document.querySelector("#save-entry");
const summaryFields = document.querySelector("#summary-fields");
const formatter = new Intl.DateTimeFormat("es-AR", {
  day: "numeric", month: "short", year: "numeric", timeZone: "UTC",
});
let endpoint;
let activeLoad;

async function api(path, options) {
  const response = await fetch(`/api/${path}`, options);
  const data = await response.json();
  if (!response.ok) {
    throw new Error(data.error || "No pudimos completar la operación.");
  }
  return data;
}

function showStatus(message = "", error = false) {
  feedback.textContent = message;
  feedback.classList.toggle("error", error);
}

function fillDate(element, value) {
  element.dateTime = value;
  element.textContent = formatter.format(new Date(value));
}

function createClassCard(entry) {
  const card = document.querySelector("#class-template").content.cloneNode(true);
  card.querySelector(".subject").textContent = entry.materia;
  fillDate(card.querySelector("time"), entry.fecha);
  card.querySelector("h3").textContent = entry.tema;
  card.querySelector(".homework").textContent = entry.tarea || "Sin tarea cargada.";
  card.querySelector(".notes").textContent = entry.apuntes || "Sin apuntes cargados.";
  return card;
}

function createRequestCard(entry) {
  const card = document.querySelector("#request-template").content.cloneNode(true);
  card.querySelector("h3").textContent = entry.materia;
  fillDate(card.querySelector("time"), entry.fecha);
  card.querySelector("button").addEventListener("click", () => openEditor("clases", entry));
  return card;
}

function renderCards(container, entries, createCard, emptyMessage) {
  if (entries.length) {
    container.replaceChildren(...entries.map(createCard));
    return;
  }
  const placeholder = document.createElement("p");
  placeholder.className = "empty";
  placeholder.textContent = emptyMessage;
  container.replaceChildren(placeholder);
}

async function refresh(message = "") {
  activeLoad?.abort();
  const controller = new AbortController();
  activeLoad = controller;
  const params = new URLSearchParams({ curso: course.value });
  if (date.value) params.set("fecha", date.value);
  clearDate.hidden = !date.value;
  showStatus("Cargando…");
  count.textContent = "";
  classList.replaceChildren();
  requestList.replaceChildren();
  try {
    const [classes, requests] = await Promise.all([
      api(`clases?${params}`, { signal: controller.signal }),
      api(`pedidos?${params}`, { signal: controller.signal }),
    ]);
    if (controller.signal.aborted) return;
    renderCards(classList, classes, createClassCard,
      "Todavía no hay resúmenes para esta selección. Podés pedir uno o compartir lo que se vio.");
    renderCards(requestList, requests, createRequestCard, "No hay pedidos pendientes.");
    count.textContent = String(classes.length);
    showStatus(message);
  } catch (error) {
    if (controller.signal.aborted) return;
    const prefix = message ? `${message} ` : "";
    showStatus(`${prefix}No pudimos cargar los datos. Volvé a intentar cambiando el filtro o recargando la página.`, true);
  }
}

function openEditor(target, entry) {
  endpoint = target;
  const sharing = target === "clases";
  form.reset();
  form.elements.curso.value = entry?.curso ?? course.value;
  form.elements.fecha.value = entry?.fecha ?? date.value;
  form.elements.materia.value = entry?.materia ?? "";
  summaryFields.hidden = !sharing;
  for (const field of summaryFields.querySelectorAll("input, textarea")) {
    field.disabled = !sharing;
  }
  form.elements.tema.required = sharing;
  document.querySelector("#editor-title").textContent = sharing ? "Compartir resumen" : "Pedir un resumen";
  saveEntry.textContent = sharing ? "Publicar resumen" : "Enviar pedido";
  entryError.textContent = "";
  editor.showModal();
}

function closeEditor() {
  if (!saveEntry.disabled) editor.close();
}

filters.addEventListener("submit", (event) => {
  event.preventDefault();
  refresh();
});
filters.addEventListener("change", () => refresh());
clearDate.addEventListener("click", () => {
  date.value = "";
  date.focus();
  refresh();
});
document.querySelector("#request-button").addEventListener("click", () => openEditor("pedidos"));
document.querySelector("#share-button").addEventListener("click", () => openEditor("clases"));
document.querySelector("#close-editor").addEventListener("click", closeEditor);
document.querySelector("#cancel-editor").addEventListener("click", closeEditor);
editor.addEventListener("cancel", (event) => {
  if (saveEntry.disabled) event.preventDefault();
});

form.addEventListener("submit", async (event) => {
  event.preventDefault();
  if (saveEntry.disabled) return;
  entryError.textContent = "";
  const data = Object.fromEntries(new FormData(form));
  saveEntry.disabled = true;
  try {
    await api(endpoint, {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify(data),
    });
    editor.close();
    course.value = data.curso;
    if (date.value && date.value !== data.fecha) date.value = data.fecha;
    refresh(endpoint === "clases" ? "Resumen publicado." : "Pedido enviado.");
  } catch (error) {
    entryError.textContent = error.message || "No pudimos guardar los cambios.";
  } finally {
    saveEntry.disabled = false;
  }
});

refresh();
