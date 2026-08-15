document.addEventListener('DOMContentLoaded', () => {
  const el = document.getElementById('footer-placeholder');
  if (!el) return;
  el.innerHTML = `
    <div class="container footer-grid">
      <div>
        <h5>The Peacekeepers' Arms Race</h5>
        <p>Testing the stability&ndash;instability paradox with cross-national panel data, 1989&ndash;2024. Originally coursework for PMDS507L (Big Data Analytics), now on a journal-submission track.</p>
      </div>
      <div>
        <h5>Project</h5>
        <a href="rq1.html">RQ1 &middot; Composition</a>
        <a href="rq2.html">RQ2 &middot; Lead-Lag</a>
        <a href="rq3.html">RQ3 &middot; Archetypes</a>
        <a href="gallery.html">Figures Gallery</a>
        <a href="paper.html">Full Paper</a>
      </div>
      <div>
        <h5>Resources</h5>
        <a href="data-methods.html">Data &amp; Methods</a>
        <a href="about.html">About &amp; Reproducibility</a>
        <a href="https://github.com/plutorion275/peacekeepers-arms-race" target="_blank" rel="noopener">GitHub Repository ↗</a>
        <a href="https://doi.org/10.5281/zenodo.21947818" target="_blank" rel="noopener">Zenodo DOI ↗</a>
      </div>
    </div>
    <div class="container footer-bottom">
      <span>T SAM DAVIS &middot; MIT LICENSE (CODE) &middot; 2026</span>
      <span>DATA VIA SIPRI &middot; UCDP &middot; V-DEM &middot; WORLD BANK &middot; CORRELATES OF WAR</span>
    </div>
  `;
});
