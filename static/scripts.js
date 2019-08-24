const statusBar = document.getElementById('status');
const authToken = new URLSearchParams(window.location.search).get('token');
const tokenParam = authToken ? `&token=${authToken}` : '';

const addStatus = statusText => {
  const status = document.createElement('em');
  status.textContent = statusText;
  statusBar.appendChild(status);

}

document.querySelectorAll('button').forEach(button => button.addEventListener('click', () => {
  const socket = button.getAttribute('socket');
  const state = button.getAttribute('state');
  const url = `/sockets?socket=${socket}&state=${state}${tokenParam}`;
  fetch(url, {method: 'POST'})
    .then(response => addStatus(response.statusText))
    .catch(e => addStatus('Error: ' + e));

  button.blur();
}));
