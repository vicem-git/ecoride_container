import '@/css/tw-output.css'
import htmx from 'htmx.org';
import { toggleHidden } from '@/js/modules/domUtils.js';
// import { toggleTheme } from '@/js/toggle-theme.js';
import 'tom-select/dist/css/tom-select.css';
import TomSelect from 'tom-select';


window.htmx = htmx;
window.toggleHidden = toggleHidden;



document.body.addEventListener("htmx:beforeSwap", () => {
  document.querySelectorAll(".dropdown").forEach((dropdown) => {
    dropdown.classList.add("hidden");
  });
});

document.body.addEventListener("htmx:afterOnLoad", (evt) => {
  const trigger = evt.detail.xhr.getResponseHeader("HX-Trigger");
  if (trigger) {
    const data = JSON.parse(trigger);
    if (data.redirectTo) {
      setTimeout(() => {
        window.location.href = data.redirectTo;
      }, 3000); // Let the user read the toast
    }
  }
});

document.addEventListener('DOMContentLoaded', () => {
  new TomSelect('#start-point-search', { create: false, maxItems: 1 });
  new TomSelect('#end-point-search', { create: false, maxItems: 1 });
});


