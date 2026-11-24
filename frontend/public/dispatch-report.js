const get = (id) => document.getElementById(id);
const form = get('report-form');
const status = get('status');
const review = get('review');
const button = get('suggest');

form.addEventListener('submit', async (event) => {
  event.preventDefault();
  review.hidden = true;
  button.disabled = true;
  status.textContent = 'Preparing draft…';

  try {
    const response = await fetch('/dispatch/report-suggestions', {
      method: 'POST',
      headers: {
        Authorization: `Bearer ${get('token').value.trim()}`,
        'Content-Type': 'application/json',
      },
      body: JSON.stringify({ report: get('report').value }),
      cache: 'no-store',
    });
    if (!response.ok) {
      status.textContent = ({
        401: 'This token expired or was rejected. Sign in again.',
        403: 'A dispatcher account is required.',
        422: 'Enter an incident report with up to 1,200 characters.',
        502: 'The model could not produce a valid draft. Review the report manually.',
        503: 'The local model or dispatch service is unavailable.',
      })[response.status] ?? 'The draft could not be generated.';
      return;
    }

    const { proposal, map_location: location } = await response.json();
    get('kind').textContent = proposal.incident_type ?? 'Needs review';
    get('severity').textContent = proposal.severity ?? 'Needs review';
    get('location').textContent = location?.label ?? 'Enter or verify a location manually';
    get('units').textContent = proposal.required_units.join(', ') || 'Needs review';
    review.hidden = false;
    status.textContent = 'Check the draft before creating an incident.';
  } catch {
    status.textContent = 'Could not connect to FastAPI.';
  } finally {
    button.disabled = false;
  }
});
