const get = (id) => document.getElementById(id);
const form = get('report-form');
const status = get('status');
const review = get('review');
const dispatchReview = get('dispatch-review');
const draftButtons = [...form.querySelectorAll('button')];
const approve = get('approve-dispatch');
const reject = get('reject-dispatch');
let pendingDraft;

class DispatchError extends Error {
  constructor(statusCode) {
    super('Dispatch request failed.');
    this.statusCode = statusCode;
  }
}

async function post(path, body, signal) {
  const response = await fetch(path, {
    method: 'POST',
    headers: {
      Authorization: `Bearer ${get('token').value.trim()}`,
      'Content-Type': 'application/json',
    },
    body: JSON.stringify(body),
    cache: 'no-store',
    signal,
  });
  if (!response.ok) throw new DispatchError(response.status);
  return response.json();
}

function message(error) {
  if (error.name === 'TimeoutError') return 'The copilot timed out. Continue in the manual dispatch API.';
  return ({
    401: 'This token expired or was rejected. Sign in again.',
    403: 'A dispatcher account is required.',
    409: 'A selected unit is unavailable or the draft was already reviewed. Check dispatch and try again.',
    422: 'Check the report or selection and try again.',
    502: 'The model could not produce a valid draft. Review the report manually.',
    503: 'The local model or dispatch service is unavailable.',
  })[error.statusCode] ?? 'Could not complete the request. Check the local service.';
}

function showDispatch(result) {
  if (result.status !== 'pending' || !result.draft_id) {
    status.textContent = result.question ?? result.reason ?? 'Review this incident manually.';
    return;
  }
  pendingDraft = result.draft_id;
  const { incident, candidates, recommended_unit_ids: recommended, alternative_unit_ids: alternatives } = result.proposal;
  get('dispatch-summary').textContent =
    `${incident.incident_type} · severity ${incident.severity} · ${incident.location_label}. ${result.proposal.rationale}`;
  const choices = get('dispatch-candidates');
  choices.replaceChildren();
  for (const candidate of candidates.filter((item) => recommended.includes(item.unit_id) || alternatives.includes(item.unit_id))) {
    const row = document.createElement('label');
    row.className = 'unit';
    const checkbox = document.createElement('input');
    checkbox.type = 'checkbox';
    checkbox.value = candidate.unit_id;
    checkbox.checked = recommended.includes(candidate.unit_id);
    const name = checkbox.checked ? 'Recommended' : 'Alternative';
    row.append(checkbox, document.createTextNode(
      `${name} · ${candidate.unit_type} ${candidate.unit_id.slice(0, 8)} · ${candidate.station} · ${candidate.eta_seconds} s modeled ETA`,
    ));
    choices.append(row);
  }
  approve.disabled = false;
  reject.disabled = false;
  get('dispatch-status').textContent = 'Review and edit the selection before approval.';
  dispatchReview.hidden = false;
  status.textContent = '';
}

form.addEventListener('submit', async (event) => {
  event.preventDefault();
  pendingDraft = null;
  review.hidden = true;
  dispatchReview.hidden = true;
  draftButtons.forEach((button) => { button.disabled = true; });
  const token = get('token').value;
  const copilot = event.submitter?.value === 'copilot';
  status.textContent = copilot ? 'Checking dispatch options…' : 'Preparing draft…';
  try {
    const data = await post(copilot ? '/dispatch/copilot/drafts' : '/dispatch/report-suggestions', {
      report: get('report').value,
    }, copilot ? AbortSignal.timeout(10000) : undefined);
    if (get('token').value !== token) return;
    if (copilot) {
      showDispatch(data);
      return;
    }
    const { proposal, map_location: location } = data;
    get('kind').textContent = proposal.incident_type ?? 'Needs review';
    get('severity').textContent = proposal.severity ?? 'Needs review';
    get('location').textContent = location?.label ?? 'Enter or verify a location manually';
    get('units').textContent = proposal.required_units.join(', ') || 'Needs review';
    review.hidden = false;
    status.textContent = 'Check the draft before creating an incident.';
  } catch (error) {
    if (get('token').value === token) status.textContent = message(error);
  } finally {
    draftButtons.forEach((button) => { button.disabled = false; });
  }
});

async function reviewDispatch(decision) {
  if (!pendingDraft) return;
  const unitIds = decision === 'approved'
    ? [...get('dispatch-candidates').querySelectorAll('input:checked')].map((checkbox) => checkbox.value)
    : [];
  const output = get('dispatch-status');
  if (decision === 'approved' && (unitIds.length < 1 || unitIds.length > 3)) {
    output.textContent = 'Select one to three units for approval.';
    return;
  }
  approve.disabled = true;
  reject.disabled = true;
  draftButtons.forEach((button) => { button.disabled = true; });
  const token = get('token').value;
  try {
    const result = await post(`/dispatch/copilot/drafts/${pendingDraft}/review`, { decision, unit_ids: unitIds });
    if (get('token').value !== token) return;
    output.textContent = result.status === 'approved'
      ? `Approved ${result.assignments.length} assignment(s) for incident ${result.incident_id}.`
      : 'Draft rejected.';
    pendingDraft = null;
  } catch (error) {
    if (get('token').value === token) output.textContent = message(error);
    approve.disabled = false;
    reject.disabled = false;
  } finally {
    draftButtons.forEach((button) => { button.disabled = false; });
  }
}

approve.addEventListener('click', () => reviewDispatch('approved'));
reject.addEventListener('click', () => reviewDispatch('rejected'));
