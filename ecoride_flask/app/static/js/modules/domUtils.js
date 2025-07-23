/**
 * Toggle the "hidden" class on the passed element
 * @param {string|HTMLElement} el - a selector string or element
 */

export function toggleHidden(el) {
  let elem = el;
  if (typeof el === 'string') {
    elem = document.getElementById(el);
  }
  if (elem) {
    elem.classList.toggle('hidden');
  }
}

document.body.addEventListener("htmx:beforeSwap", () => {
  document.querySelectorAll(".dropdown").forEach((dropdown) => {
    dropdown.classList.add("hidden");
  });
});
