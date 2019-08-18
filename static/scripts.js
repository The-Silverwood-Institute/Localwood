const statusBar = document.getElementById('status');

const addStatus = statusText => {
  const status = document.createElement('em');
  status.textContent = statusText;
  statusBar.appendChild(status);

}

document.querySelectorAll('button').forEach(button => button.addEventListener('click', () => {
  const socket = button.getAttribute('socket');
  const state = button.getAttribute('state');
  fetch(`/sockets?socket=${socket}&state=${state}`, {method: 'POST'})
    .then(response => addStatus(response.statusText))
    .catch(e => addStatus('Error: ' + e));
}));
