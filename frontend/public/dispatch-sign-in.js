const get = (id) => document.getElementById(id);
const form = get('account-sign-in');
const button = get('email-sign-in');
const signOut = get('account-sign-out');
const status = get('identity-status');
const tokenField = get('token');
let rescueToken = '';

function clearSession() {
  rescueToken = '';
  tokenField.value = '';
  get('report-form').hidden = true;
  get('review').hidden = true;
  get('dispatch-review').hidden = true;
  get('rescue-assignment').hidden = true;
  get('rescue-units').replaceChildren();
  get('status').textContent = '';
  get('report').value = '';
  form.hidden = false;
  signOut.hidden = true;
}

async function loadAssignments(token) {
  const response = await fetch('/dispatch/board', { headers: { Authorization: `Bearer ${token}` }, cache: 'no-store' });
  if (!response.ok) throw new Error('The rescue assignment could not be loaded.');
  const { units } = await response.json();
  if (rescueToken !== token) return;
  const list = get('rescue-units');
  list.replaceChildren();
  for (const unit of units) {
    const row = document.createElement('li');
    row.textContent = `${unit.unit_type} unit ${unit.unit_id.slice(0, 8)} · ${unit.incident_id ? 'Active assignment' : 'Available'}`;
    list.append(row);
  }
  if (!units.length) list.textContent = 'An administrator can configure your rescue unit.';
  get('rescue-assignment').hidden = false;
}

get('refresh-rescue').addEventListener('click', async (event) => {
  const control = event.currentTarget;
  const token = rescueToken;
  if (!token) return;
  control.disabled = true;
  try {
    await loadAssignments(token);
  } catch (error) {
    if (rescueToken === token) status.textContent = error.message;
  } finally {
    control.disabled = false;
  }
});

signOut.addEventListener('click', () => {
  clearSession();
  status.textContent = 'Signed out of this page.';
});

form.addEventListener('submit', async (event) => {
  event.preventDefault();
  button.disabled = true;
  status.textContent = 'Signing in…';
  try {
    const config = await fetch('/dispatch/auth-config', { cache: 'no-store' });
    if (!config.ok) throw new Error('The local sign-in configuration is unavailable.');
    const { project_url: base, publishable_key: key } = await config.json();
    const login = await fetch(new URL('auth/v1/token?grant_type=password', base), {
      method: 'POST',
      redirect: 'error',
      cache: 'no-store',
      headers: { apikey: key, 'Content-Type': 'application/json' },
      body: JSON.stringify({ email: get('account-email').value.trim(), password: get('account-password').value }),
    });
    if (!login.ok) throw new Error('Supabase rejected the sign-in. Check the email and password.');
    const { access_token: token } = await login.json();
    const headers = { Authorization: `Bearer ${token}` };
    const identity = await fetch('/dispatch/me', { headers, cache: 'no-store' });
    if (identity.status === 403) throw new Error('Signed in successfully. Ask the project admin to enroll this account.');
    if (!identity.ok) throw new Error('The app could not verify your ClearPath role.');
    const { role } = await identity.json();
    if (role === 'dispatcher') {
      tokenField.value = token;
      get('report-form').hidden = false;
    } else if (role === 'rescue') {
      rescueToken = token;
      await loadAssignments(token);
    }
    status.textContent = `Signed in as ${role}.`;
    form.hidden = true;
    signOut.hidden = false;
  } catch (error) {
    clearSession();
    status.textContent = error.message;
  } finally {
    get('account-password').value = '';
    button.disabled = false;
  }
});
