document.addEventListener('DOMContentLoaded', () => {
  const categories = document.querySelectorAll('.category');
  categories.forEach(el => {
    el.addEventListener('click', () => {
      const theme = el.getAttribute('data-theme');
      window.location.href = `/quest?theme=${encodeURIComponent(theme)}`;
    });
  });
});
