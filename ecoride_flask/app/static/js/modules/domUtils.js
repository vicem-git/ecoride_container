

export function toggleHidden(el) {
  let elem = el;
  if (typeof el === 'string') {
    elem = document.getElementById(el);
  }
  if (elem) {
    elem.classList.toggle('hidden');
  }
}


