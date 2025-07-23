import '@/css/tw-output.css'
import htmx from 'htmx.org';
import { toggleHidden } from '@/js/modules/domUtils.js';
// import { toggleTheme } from '@/js/toggle-theme.js';
import 'tom-select/dist/css/tom-select.css';
import TomSelect from 'tom-select';


window.htmx = htmx;
window.toggleHidden = toggleHidden;

// Initialize TomSelect after DOM is ready
document.addEventListener('DOMContentLoaded', () => {
  new TomSelect('#start-point-search', { create: false, maxItems: 1 });
  new TomSelect('#end-point-search', { create: false, maxItems: 1 });
});
