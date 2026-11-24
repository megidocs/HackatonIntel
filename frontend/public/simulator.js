import { Map as MapLibreMap, Marker, NavigationControl } from "/sim/vendor/maplibre-gl.mjs";

const $ = (selector) => document.querySelector(selector);
const telAviv = location.pathname === "/simulator/tel-aviv";
const incidentForm = $("#incident-setup");
const incidentSelect = $("#incident-location");
let scenario;
const map = new MapLibreMap({
  container: "map",
  center: [-73.978, 40.761],
  zoom: 13.55,
  minZoom: 11.5,
  maxZoom: 18.5,
  dragRotate: false,
  pitchWithRotate: false,
  style: {
    version: 8,
    sources: {},
    layers: [{ id: "water", type: "background", paint: { "background-color": "#101e29" } }],
  },
});
map.addControl(new NavigationControl({ showCompass: false }), "top-right");

const canvas = $("#vehicles");
const context = canvas.getContext("2d");
const frameMeter = new URLSearchParams(location.search).has("measureFrames") ? $("#frame-meter") : null;
const frameIntervals = [];
let lastMeasuredFrame = null;
let measuredDensity = null;
let measurementStart = 0;
if (frameMeter) {
  frameMeter.hidden = false;
  frameMeter.textContent = "Start playback to measure frames";
  document.addEventListener("visibilitychange", clearFrameMeasurement);
}
const controls = [...document.querySelectorAll(".sidebar button, .sidebar input, .sidebar select")]
  .filter((control) => !control.closest("#presenter-access"));
let presenterToken = "";
let pollTimer;
let polling = false;
let state;
let mode;
let previousVehicles = new Map();
let frameVehicles = [];
let frameStart = 0;
let routeKey = "";
let closureKey = null;
let priorityKey = "";
let signalTime = -1;
let requestNumber = 0;
let appliedRequest = 0;
let reconnecting = false;

const point = (coordinates, properties) => ({
  type: "Feature",
  geometry: { type: "Point", coordinates },
  properties,
});
const collection = (features) => ({ type: "FeatureCollection", features });
const empty = collection([]);

function addLayers(data) {
  scenario = data.scenario;
  $("#city-name").textContent = scenario.name;
  $("#map").setAttribute("aria-label", `${scenario.name} street map`);
  $(".map-area").setAttribute("aria-label", `Interactive ${scenario.name} road map`);
  document.title = `ClearPath AI — ${scenario.name} Traffic Simulator`;
  if (telAviv) {
    $('.city-links [aria-current]').removeAttribute("aria-current");
    $('.city-links a[href="/simulator/tel-aviv"]').setAttribute("aria-current", "page");
  }
  for (const place of scenario.incidents) {
    incidentSelect.add(new Option(`${place.name} · ${place.hebrew}`, place.name));
  }
  incidentForm.hidden = !scenario.incidents.length;
  if (scenario.bounds) {
    map.fitBounds(scenario.bounds, { padding: 40, duration: 0 });
  }

  map.addSource("land", { type: "geojson", data: data.land });
  map.addLayer({
    id: "land", type: "fill", source: "land",
    paint: { "fill-color": "#1b2830", "fill-outline-color": "#30424d" },
  });
  map.addSource("roads", {
    type: "geojson", data: data.roads,
    attribution: '© <a href="https://www.openstreetmap.org/copyright">OpenStreetMap contributors</a>',
  });
  const major = ["match", ["get", "kind"], ["motorway", "trunk", "primary", "secondary"], true, false];
  map.addLayer({
    id: "streets", type: "line", source: "roads",
    layout: { "line-join": "round", "line-cap": "round" },
    paint: {
      "line-color": ["case", major, "#708694", "#435965"],
      "line-width": ["interpolate", ["linear"], ["zoom"], 12, .65, 15, 1.6, 18, 3.8],
      "line-opacity": .86,
    },
  });
  map.addLayer({
    id: "street-hit", type: "line", source: "roads",
    paint: { "line-color": "#000000", "line-opacity": 0, "line-width": 12 },
  });

  map.addSource("signals", { type: "geojson", data: data.signals });
  map.addLayer({
    id: "signal-points", type: "circle", source: "signals", minzoom: 12.5,
    paint: {
      "circle-color": "#e67780",
      "circle-radius": ["interpolate", ["linear"], ["zoom"], 13, 1.35, 15, 2.4, 17, 4],
      "circle-opacity": ["interpolate", ["linear"], ["zoom"], 12.5, .4, 15, .88],
      "circle-stroke-color": "#19252d", "circle-stroke-width": .65,
    },
  });
  map.addSource("corridor", { type: "geojson", data: empty });
  map.addLayer({
    id: "alert-corridor", type: "line", source: "corridor",
    layout: { "line-cap": "round", "line-join": "round" },
    paint: {
      "line-color": "#65e0ce",
      "line-width": ["interpolate", ["linear"], ["zoom"], 12, 14, 14, 21, 17, 43],
      "line-opacity": .23,
    },
  });
  map.addSource("route", { type: "geojson", data: empty });
  for (const [id, color, width] of [["route-halo", "#102522", 9], ["route-line", "#65e0ce", 4]]) {
    map.addLayer({
      id, type: "line", source: "route",
      layout: { "line-cap": "round", "line-join": "round" },
      paint: { "line-width": width, "line-color": color, "line-opacity": .97 },
    });
  }
  map.addLayer({
    id: "closed-roads", type: "line", source: "roads", filter: ["==", ["get", "segment"], -1],
    paint: { "line-color": "#ffad68", "line-width": 5, "line-dasharray": [1, 1.3] },
  });
  map.addSource("priority-signals", { type: "geojson", data: empty });
  map.addLayer({
    id: "priority-points", type: "circle", source: "priority-signals",
    paint: {
      "circle-color": ["case", ["==", ["get", "phase"], "priority"], "#65e0ce", "#ffd683"],
      "circle-radius": 5, "circle-stroke-width": 1.5, "circle-stroke-color": "#142328",
    },
  });
  map.addSource("endpoints", { type: "geojson", data: empty });
  map.addLayer({
    id: "route-endpoints", type: "circle", source: "endpoints",
    paint: {
      "circle-radius": 6, "circle-color": ["get", "color"],
      "circle-stroke-color": "#13222c", "circle-stroke-width": 2,
    },
  });

  for (const { name, hebrew, coordinates } of scenario.landmarks) {
    const label = document.createElement("span");
    label.className = hebrew ? "map-label map-landmark" : "map-label";
    label.textContent = hebrew || name;
    if (hebrew) label.lang = "he";
    const options = hebrew ? { anchor: "bottom", offset: [0, -8] } : {};
    new Marker({ element: label, ...options }).setLngLat(coordinates).addTo(map);
  }
}

async function request(path, payload, token = presenterToken) {
  const options = { headers: {} };
  if (payload !== undefined) {
    options.method = "POST";
    options.headers["Content-Type"] = "application/json";
    options.body = JSON.stringify(payload);
  }
  if (token && (path === "/simulation/access" || (payload !== undefined && path.startsWith("/simulation/")))) {
    options.headers["X-ClearPath-Control-Token"] = token;
  }
  const url = telAviv && path !== "/simulation/access" ? path.replace("/simulation/", "/simulation/tel-aviv/") : path;
  const response = await fetch(url, options);
  if (!response.ok) {
    const { detail } = await response.json().catch(() => ({}));
    throw new Error(typeof detail === "string" ? detail : "The simulator could not complete this request.");
  }
  return response.json();
}

function locationLabel(coordinates, defaultName, defaultPoint) {
  return coordinates.join() === defaultPoint.join()
    ? defaultName
    : [coordinates[1], coordinates[0]].map((coord) => coord.toFixed(4)).join(", ");
}

function clockText(seconds) {
  const whole = Math.floor(seconds);
  return [Math.floor(whole / 60), whole % 60].map((value) => String(value).padStart(2, "0")).join(":");
}

function showState(next) {
  const waiting = next.route_status === "awaiting_dispatch";
  const newDispatch = next.dispatch_mode && !waiting && (state?.route_status === "awaiting_dispatch" ||
    state?.destination.join() !== next.destination.join() || state?.origin.join() !== next.origin.join());
  const first = !state;
  const now = performance.now();
  const mix = Math.min(1, (now - frameStart) / 210);
  const old = new Map();
  for (const car of frameVehicles) {
    const from = previousVehicles.get(car.id) ?? car.point;
    old.set(car.id, interpolate(from, car.point, mix));
  }
  previousVehicles = next.time < (state?.time ?? 0) ? new Map() : old;
  frameVehicles = next.vehicles;
  frameStart = now;
  state = next;

  $("#demo-type").textContent = next.dispatch_mode ? "Dispatch-driven demo" : "Traffic simulator demo";
  $(".endpoints").hidden = Boolean(next.dispatch_mode);
  const key = JSON.stringify([next.origin, next.destination, next.route, next.dispatch_destination]);
  if (key !== routeKey) {
    routeKey = key;
    map.getSource("route").setData(collection(next.route.length >= 2 ? [{
      type: "Feature", geometry: { type: "LineString", coordinates: next.route }, properties: {},
    }] : []));
    map.getSource("endpoints").setData(collection(waiting ? [] : [
      point(next.origin, { color: "#65e0ce" }), point(next.destination, { color: "#ffad68" }),
    ]));
    $("#origin-label").textContent = locationLabel(next.origin, scenario.origin, next.default_origin);
    const incident = scenario.incidents.find((place) => place.point.join() === next.destination.join());
    incidentSelect.value = incident?.name ?? "";
    $("#destination-label").textContent = incident?.name ??
      locationLabel(next.destination, scenario.destination, next.default_destination);
    if ((first && !scenario.bounds) || newDispatch) {
      const [x, y] = next.origin;
      const [otherX, otherY] = next.destination;
      map.fitBounds(
        [[Math.min(x, otherX), Math.min(y, otherY)], [Math.max(x, otherX), Math.max(y, otherY)]],
        { padding: 76, maxZoom: 13.45, duration: 0 },
      );
    }
  }
  const closureList = next.closures.join();
  if (closureList !== closureKey) {
    closureKey = closureList;
    map.setFilter("closed-roads", ["in", ["get", "segment"], ["literal", next.closures]]);
  }
  const priorityStateKey = JSON.stringify([next.corridor, next.priority_signals]);
  if (priorityStateKey !== priorityKey) {
    priorityKey = priorityStateKey;
    map.getSource("corridor").setData(collection(next.corridor.length >= 2 ? [{
      type: "Feature", geometry: { type: "LineString", coordinates: next.corridor }, properties: {},
    }] : []));
    map.getSource("priority-signals").setData(collection(
      next.priority_signals.map((signal) => point(signal.point, { phase: signal.phase })),
    ));
  }
  const second = Math.floor(next.time);
  if (signalTime !== second) {
    signalTime = second;
    const phase = ["%", ["+", ["get", "offset"], second], 24];
    map.setPaintProperty("signal-points", "circle-color", [
      "case", ["<", phase, 10], "#6ed9aa", ["<", phase, 12], "#ffd683",
      ["<", phase, 22], "#e67780", "#ffd683",
    ]);
  }

  $("#clock").textContent = clockText(next.time);
  $("#connection").dataset.state = next.running ? "running" : "paused";
  $("#connection-text").textContent = next.running ? "Running" : "Paused";
  $("#play-text").textContent = next.running ? "Pause" : next.time > 0 ? "Resume" : next.dispatch_mode ? "Start traffic" : "Start simulation";
  $("#play > span:first-child").textContent = next.running ? "Ⅱ" : "▶";
  $("#closure-count").textContent = next.closures.length;
  $("#priority").checked = next.priority_enabled;
  $("#priority-count").textContent = next.priority_signals.length;
  $("#alert-count").textContent = next.alerted_count;
  $("#distance").textContent = next.route_status === "blocked" ? "—" : `${(next.route_meters / 1000).toFixed(2)} km`;
  $("#eta").textContent = next.route_status === "blocked" ? "—" : `${(next.route_seconds / 60).toFixed(1)} min`;
  $(".route-metrics").hidden = waiting;
  const status = {
    awaiting_dispatch: "Waiting for an approved dispatch.",
    blocked: "No open route to the destination.",
    arrived: `Arrived in ${clockText(next.arrival_time ?? 0)} simulated time.`,
    en_route: next.dispatch_mode ? `En route${next.dispatch_destination ? ` to ${next.dispatch_destination}` : ""}.` : "",
  };
  const routeStatus = status[next.route_status] ?? "";
  if ($("#route-status").textContent !== routeStatus) $("#route-status").textContent = routeStatus;
  if (document.activeElement !== $("#density")) {
    $("#density").value = next.density;
    $("#density-output").textContent = next.density;
  }
  $("#speed").value = next.speed;
}

async function refresh(path, payload) {
  const order = ++requestNumber;
  try {
    const next = await request(path, payload);
    if (order < appliedRequest) return null;
    appliedRequest = order;
    showState(next);
    if (reconnecting) {
      reconnecting = false;
      setMode(mode);
    }
    return next;
  } catch (error) {
    if (payload === undefined && path === "/simulation/state") {
      reconnecting = true;
      $("#connection").dataset.state = "error";
      $("#connection-text").textContent = "Reconnecting";
      error = new Error("Waiting for the local simulator to respond.");
    }
    $("#map-message").textContent = error.message;
    return null;
  }
}

function interpolate(a, b, time) {
  return [a[0] + (b[0] - a[0]) * time, a[1] + (b[1] - a[1]) * time];
}

function clearFrameMeasurement() {
  frameIntervals.length = 0;
  lastMeasuredFrame = null;
}

function measureFrame(now) {
  if (!state?.running || document.hidden || measuredDensity !== state.density) {
    clearFrameMeasurement();
    measuredDensity = state?.density;
    return;
  }
  if (lastMeasuredFrame === null) {
    measurementStart = now;
    lastMeasuredFrame = now;
    return;
  }
  frameIntervals.push(now - lastMeasuredFrame);
  lastMeasuredFrame = now;
  if (now - measurementStart >= 10_000) {
    const frames = frameIntervals.length;
    const fps = frames * 1000 / (now - measurementStart);
    frameIntervals.sort((a, b) => a - b);
    const p95 = frameIntervals[Math.ceil(frames * .95) - 1];
    frameMeter.textContent = `${fps.toFixed(1)} FPS · p95 ${p95.toFixed(1)} ms · ${measuredDensity} cars`;
    frameIntervals.length = 0;
    measurementStart = now;
  }
}

function drawVehicles(now) {
  const width = canvas.clientWidth;
  const height = canvas.clientHeight;
  const scale = Math.min(devicePixelRatio, 2);
  if (canvas.width !== Math.round(width * scale) || canvas.height !== Math.round(height * scale)) {
    canvas.width = Math.round(width * scale);
    canvas.height = Math.round(height * scale);
  }
  context.setTransform(scale, 0, 0, scale, 0, 0);
  context.clearRect(0, 0, width, height);
  const mix = Math.min(1, (now - frameStart) / 210);
  const moving = new Path2D();
  const stopped = new Path2D();
  const yielding = new Path2D();
  let emergency;
  for (const car of frameVehicles) {
    const before = previousVehicles.get(car.id) ?? car.point;
    const screen = map.project(interpolate(before, car.point, mix));
    if (screen.x < -10 || screen.y < -10 || screen.x > width + 10 || screen.y > height + 10) continue;
    if (car.id === 0) emergency = screen;
    else {
      const path = car.alerted ? yielding : car.stopped ? stopped : moving;
      path.moveTo(screen.x + 2, screen.y);
      path.arc(screen.x, screen.y, 2, 0, Math.PI * 2);
    }
  }
  context.fillStyle = "#a8c0d7";
  context.fill(moving);
  context.fillStyle = "#7e91a0";
  context.fill(stopped);
  context.fillStyle = "#ffd683";
  context.fill(yielding);
  if (emergency) {
    context.beginPath();
    context.arc(emergency.x, emergency.y, 6, 0, Math.PI * 2);
    context.fillStyle = "#65e0ce";
    context.fill();
    context.lineWidth = 2;
    context.strokeStyle = "#092d2a";
    context.stroke();
  }
  if (frameMeter) measureFrame(now);
  requestAnimationFrame(drawVehicles);
}

const instructions = {
  origin: "Click a street location to set the rescue vehicle origin.",
  destination: "Click a street location to set the incident destination.",
  closure: "Click a road to close it. Click a closed road to reopen it.",
};

function setMode(next) {
  mode = next;
  for (const button of document.querySelectorAll("[data-mode]")) {
    button.setAttribute("aria-pressed", String(button.dataset.mode === next));
  }
  map.getCanvas().style.cursor = next ? "crosshair" : "";
  $("#map-message").textContent = instructions[next] ?? "";
}

function closestRoad(pixel) {
  let nearest;
  let distanceSquared = Infinity;
  for (const street of map.queryRenderedFeatures(pixel, { layers: ["street-hit"] })) {
    const geometry = street.geometry;
    const lines = geometry.type === "LineString" ? [geometry.coordinates] : geometry.coordinates;
    for (const line of lines) {
      const points = line.map((coordinate) => map.project(coordinate));
      for (let index = 1; index < points.length; index++) {
        const a = points[index - 1];
        const b = points[index];
        const dx = b.x - a.x;
        const dy = b.y - a.y;
        const projection = ((pixel.x - a.x) * dx + (pixel.y - a.y) * dy) / (dx * dx + dy * dy || 1);
        const factor = Math.max(0, Math.min(1, projection));
        const distance = (pixel.x - a.x - factor * dx) ** 2 + (pixel.y - a.y - factor * dy) ** 2;
        if (distance < distanceSquared) {
          distanceSquared = distance;
          nearest = street;
        }
      }
    }
  }
  return nearest;
}

map.on("load", async () => {
  try {
    addLayers(await request("/simulation/map"));
    const access = await request("/simulation/access");
    await refresh("/simulation/state");
    if (!reconnecting) setMode();
    $("#presenter-access").hidden = !access.restricted;
    for (const control of controls) control.disabled = !access.allowed;
    requestAnimationFrame(drawVehicles);
  } catch (error) {
    $("#map-message").textContent = error.message;
    return;
  }

  schedulePoll();
});

function schedulePoll() {
  if (!document.hidden) pollTimer = setTimeout(poll, state?.running ? 200 : 1500);
}

async function poll() {
  if (document.hidden || polling) return;
  polling = true;
  try {
    await refresh("/simulation/state");
  } finally {
    polling = false;
    schedulePoll();
  }
}

document.addEventListener("visibilitychange", () => {
  clearTimeout(pollTimer);
  if (!document.hidden && state) poll();
});

$("#presenter-access").addEventListener("submit", async (event) => {
  event.preventDefault();
  const field = $("#presenter-token");
  try {
    const access = await request("/simulation/access", undefined, field.value);
    if (!access.allowed) {
      $("#presenter-status").textContent = "That presenter code did not match.";
      return;
    }
    presenterToken = field.value;
    field.value = "";
    $("#presenter-status").textContent = "Presenter controls unlocked for this tab.";
    for (const control of controls) control.disabled = false;
  } catch (error) {
    $("#presenter-status").textContent = error.message;
  }
});

for (const button of document.querySelectorAll("[data-mode]")) {
  button.disabled = true;
  button.addEventListener("click", () => setMode(mode === button.dataset.mode ? null : button.dataset.mode));
}
map.on("click", async ({ point: pixel, lngLat }) => {
  if (mode === "closure") {
    const street = closestRoad(pixel);
    if (!street) {
      $("#map-message").textContent = "Click a drivable road to toggle its closure.";
      return;
    }
    const next = await refresh(`/simulation/closure/${street.properties.segment}`, {});
    if (next && mode === "closure") {
      const closed = next.closures.includes(street.properties.segment);
      $("#map-message").textContent = `${street.properties.name} ${closed ? "closed" : "reopened"}. Click another road or press Escape.`;
    }
  } else if (mode) {
    const target = mode;
    setMode();
    refresh("/simulation/point", { target, lat: lngLat.lat, lon: lngLat.lng });
  }
});
$("#play").addEventListener("click", () => refresh("/simulation/control", { running: !state?.running }));
$("#reset").addEventListener("click", () => {
  setMode();
  refresh("/simulation/control", { reset: true });
});
incidentForm.addEventListener("submit", (event) => {
  event.preventDefault();
  const incident = scenario.incidents.find((place) => place.name === incidentSelect.value);
  if (!incident) return;
  const [lon, lat] = incident.point;
  setMode();
  refresh("/simulation/point", { target: "destination", lat, lon });
});
$("#density").addEventListener("input", (event) => { $("#density-output").textContent = event.target.value; });
$("#density").addEventListener("change", (event) => refresh("/simulation/control", { density: Number(event.target.value) }));
$("#speed").addEventListener("change", (event) => refresh("/simulation/control", { speed: Number(event.target.value) }));
$("#priority").addEventListener("change", (event) => refresh("/simulation/control", { priority: event.target.checked }));
document.addEventListener("keydown", (event) => { if (event.key === "Escape" && mode) setMode(); });
