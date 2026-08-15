// Nav toggle
document.addEventListener('DOMContentLoaded', () => {
  const toggle = document.querySelector('.nav-toggle');
  const links = document.querySelector('.nav-links');
  if (toggle && links) {
    toggle.addEventListener('click', () => links.classList.toggle('open'));
    links.querySelectorAll('a').forEach(a => a.addEventListener('click', () => links.classList.remove('open')));
  }

  // Scroll reveal
  const revealables = document.querySelectorAll('.card, figure.plate, .arche, .case-step, .hyp, .incident, .source, .stat');
  if ('IntersectionObserver' in window) {
    const io = new IntersectionObserver((entries) => {
      entries.forEach(e => {
        if (e.isIntersecting) {
          e.target.style.transition = 'opacity .5s ease, transform .5s ease';
          e.target.style.opacity = '1';
          e.target.style.transform = 'translateY(0)';
          io.unobserve(e.target);
        }
      });
    }, { threshold: 0.08, rootMargin: '0px 0px -40px 0px' });
    revealables.forEach(el => {
      el.style.opacity = '0';
      el.style.transform = 'translateY(14px)';
      io.observe(el);
    });
  }

  // Gallery lightbox + filter
  const grid = document.querySelector('.gallery-grid');
  if (grid) {
    const lb = document.getElementById('lightbox');
    const lbImg = lb.querySelector('img');
    const lbCap = lb.querySelector('.lb-cap');
    grid.addEventListener('click', (e) => {
      const item = e.target.closest('.gallery-item');
      if (!item) return;
      const img = item.querySelector('img');
      lbImg.src = img.src;
      lbImg.alt = img.alt;
      lbCap.textContent = item.dataset.caption || img.alt;
      lb.classList.add('open');
    });
    lb.addEventListener('click', (e) => {
      if (e.target === lb || e.target.classList.contains('lb-close')) lb.classList.remove('open');
    });
    document.addEventListener('keydown', (e) => { if (e.key === 'Escape') lb.classList.remove('open'); });

    const filterBar = document.querySelector('.filter-bar');
    if (filterBar) {
      filterBar.addEventListener('click', (e) => {
        const btn = e.target.closest('.filter-btn');
        if (!btn) return;
        filterBar.querySelectorAll('.filter-btn').forEach(b => b.classList.remove('active'));
        btn.classList.add('active');
        const f = btn.dataset.filter;
        grid.querySelectorAll('.gallery-item').forEach(item => {
          item.style.display = (f === 'all' || item.dataset.group === f) ? '' : 'none';
        });
      });
    }
  }
});
