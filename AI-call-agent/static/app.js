const form = document.querySelector('#call-form');
const phoneInput = document.querySelector('#phone');
const button = document.querySelector('#call-button');
const status = document.querySelector('#status');
const loader = document.querySelector('#loader');

function setStatus(message, kind = '') {
  status.textContent = message;
  status.className = `status ${kind}`;
}

form.addEventListener('submit', async (event) => {
  event.preventDefault();
  const phone = phoneInput.value.trim();
  if (!/^\+[1-9]\d{7,14}$/.test(phone)) {
    setStatus('Use international format, for example +91XXXXXXXXXX.', 'error');
    phoneInput.focus();
    return;
  }
  button.disabled = true;
  loader.classList.add('active');
  setStatus('Connecting to Twilio...', 'connecting');
  try {
    const response = await fetch('/trigger_call', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ phone })
    });
    const data = await response.json();
    if (!response.ok) throw new Error(data.error || 'Unable to start the call.');
    setStatus(`Call started. SID: ${data.call_sid}`, 'success');
  } catch (error) {
    setStatus(error.message, 'error');
  } finally {
    button.disabled = false;
    loader.classList.remove('active');
  }
});
