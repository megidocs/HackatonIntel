import { Marker } from "/sim/vendor/maplibre-gl.mjs";

export function setupDispatchPanel(map, locations, request, refresh) {
  const byId = (id) => document.getElementById(id);
  const report = byId("dispatch-form");
  const review = byId("dispatch-review");
  const location = byId("dispatch-location");
  const unitSelection = byId("dispatch-unit");
  const feedback = byId("dispatch-feedback");
  const fleetList = byId("fleet-units");
  const markers = new Map();
  let allowed = false;
  let submitting = false;
  let active = false;
  let proposal;

  for (const place of locations) {
    location.add(new Option(`${place.name} · ${place.hebrew}`, place.name));
  }
  byId("dispatch-workflow").hidden = false;

  function updateControls() {
    byId("report-fields").disabled = !allowed || submitting;
    byId("review-fields").disabled = !allowed || submitting || active;
  }

  function clearReview() {
    proposal = null;
    review.hidden = true;
  }

  report.addEventListener("input", () => {
    clearReview();
    feedback.textContent = "";
  });

  report.addEventListener("submit", async (event) => {
    event.preventDefault();
    clearReview();
    submitting = true;
    updateControls();
    feedback.textContent = "Checking available vehicles…";
    const payload = {
      report: byId("dispatch-report").value,
      location: location.value,
      unit_type: byId("dispatch-type").value,
    };
    try {
      const result = await request("/simulation/propose", payload);
      if (!result.candidates.length) {
        feedback.textContent = "No available vehicle of that type has an open route to this location.";
        return;
      }
      proposal = { ...payload, version: result.version };
      byId("review-report").textContent = payload.report;
      unitSelection.replaceChildren(...result.candidates.map((unit) =>
        new Option(`${unit.name} · ${unit.base} · ${unit.eta_seconds} s`, unit.id)));
      review.hidden = false;
      feedback.textContent = active
        ? "Review the options now. Approve after the current vehicle arrives."
        : "Review the available vehicles and approve one to start the trip.";
    } catch (error) {
      feedback.textContent = error.message;
    } finally {
      submitting = false;
      updateControls();
    }
  });

  review.addEventListener("submit", async (event) => {
    event.preventDefault();
    if (!proposal || active || submitting) return;
    submitting = true;
    updateControls();
    try {
      await request("/simulation/approve", { ...proposal, unit_id: unitSelection.value });
      clearReview();
      report.reset();
      feedback.textContent = "";
      await refresh("/simulation/state");
    } catch (error) {
      feedback.textContent = error.message;
    } finally {
      submitting = false;
      updateControls();
    }
  });

  let fleetKey;
  return {
    setAllowed(value) {
      allowed = value;
      updateControls();
    },
    show(state) {
      const wasActive = active;
      active = state.fleet.some((unit) => !unit.available);
      updateControls();
      if (proposal && proposal.version !== state.dispatch_version) clearReview();
      if (proposal && wasActive && !active) {
        feedback.textContent = "The current vehicle has arrived. You can approve the reviewed dispatch.";
      }
      const unit = state.fleet.find((item) => item.id === state.dispatched_unit);
      const trip = byId("fleet-trip");
      const statusText = unit ? {
        en_route: `${unit.name} is en route to ${state.dispatch_destination}.`,
        blocked: `${unit.name} is waiting for an open route to ${state.dispatch_destination}.`,
        arrived: `${unit.name} reached ${state.dispatch_destination} and is available again.`,
      }[state.route_status] : "";
      if (trip.textContent !== statusText) trip.textContent = statusText;
      const key = state.fleet.map((unit) => unit.available).join();
      if (key === fleetKey) return;
      fleetKey = key;
      byId("fleet-count").textContent = `${state.fleet.filter((unit) => unit.available).length} available`;
      fleetList.replaceChildren(...state.fleet.map((unit) => {
        if (!markers.has(unit.id)) {
          const marker = document.createElement("span");
          marker.className = "fleet-marker";
          marker.textContent = unit.hebrew;
          marker.lang = "he";
          marker.title = `${unit.name} · ${unit.base}`;
          new Marker({ element: marker, anchor: "bottom", offset: [0, -3] }).setLngLat(unit.point).addTo(map);
          markers.set(unit.id, marker);
        }
        markers.get(unit.id).dataset.available = unit.available;
        const row = document.createElement("li");
        const label = document.createElement("strong");
        label.textContent = unit.name;
        const status = document.createElement("span");
        status.className = "fleet-status";
        status.dataset.available = unit.available;
        status.textContent = unit.available ? "Available" : "Dispatched";
        const base = document.createElement("span");
        base.className = "fleet-base";
        base.textContent = `${unit.base} · ${unit.hebrew}`;
        row.append(label, status, base);
        return row;
      }));
    },
  };
}
