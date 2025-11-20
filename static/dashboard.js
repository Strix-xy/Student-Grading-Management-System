// dashboard.js - client-side dashboard behavior
(function () {
  function safeParse(jsonText) {
    try {
      return JSON.parse(jsonText || '[]');
    } catch (e) {
      console.error('Failed to parse dashboard JSON', e);
      return [];
    }
  }

  function fetchAndRenderStats() {
    fetch('/api/stats')
      .then(res => res.json())
      .then(data => {
        const avgEl = document.getElementById('avgGrade');
        const passingEl = document.getElementById('passingRate');
        const bar = document.getElementById('passingBar');
        if (avgEl && data.avg_grade !== undefined) avgEl.textContent = Number(data.avg_grade).toFixed(2);
        if (passingEl && data.passing_rate !== undefined) passingEl.textContent = data.passing_rate + '%';
        if (bar && data.passing_rate !== undefined) bar.style.width = data.passing_rate + '%';
      })
      .catch(err => console.error('Error fetching stats:', err));
  }

  function getRecentGrades() {
    const el = document.getElementById('recentGradesData');
    if (!el) return [];
    return safeParse(el.textContent || el.innerText);
  }

  function populateClassOptions(recentGrades) {
    const classSet = new Set();
    recentGrades.forEach(g => {
      if (g.subject_class_year) classSet.add(g.subject_class_year);
      if (g.student_school_year) classSet.add(g.student_school_year);
    });
    const sel = document.getElementById('dashboardClass');
    if (!sel) return;
    // remove previous non-default options
    Array.from(sel.options).forEach(o => { if (o.value) o.remove(); });
    Array.from(classSet).sort().forEach(c => {
      const opt = document.createElement('option');
      opt.value = c; opt.textContent = c; sel.appendChild(opt);
    });
  }

  function renderRecentGrades(recentGrades) {
    const tbody = document.querySelector('table tbody');
    if (!tbody) return;
    tbody.innerHTML = '';
    if (!recentGrades || !recentGrades.length) {
      const tr = document.createElement('tr');
      tr.innerHTML = '<td colspan="4" class="px-4 py-8 text-center text-text-muted"><i data-lucide="inbox" class="w-12 h-12 mx-auto mb-2 opacity-50"></i><p>No matching grades</p></td>';
      tbody.appendChild(tr);
      return;
    }
    recentGrades.forEach(g => {
      const tr = document.createElement('tr');
      tr.className = 'border-b border-gray-100 hover:bg-gray-50 transition-colors';
      const studentName = g.student_name || (g.first_name && g.last_name ? (g.first_name + ' ' + g.last_name) : '');
      const studentId = g.student_id || g.sid || '';
      const subj = g.subject_code || '';
      const gradeVal = (g.final_grade !== undefined && g.final_grade !== null) ? Number(g.final_grade).toFixed(2) : '';
      const passed = (g.final_grade !== undefined && g.final_grade >= 75);
      tr.innerHTML = `
        <td class="px-4 py-3">
          <div class="font-medium text-text-dark">${studentName}</div>
          <div class="text-xs text-text-muted">${studentId}</div>
        </td>
        <td class="px-4 py-3 text-sm text-text-dark">${subj}</td>
        <td class="px-4 py-3"><span class="text-lg font-bold">${gradeVal}</span></td>
        <td class="px-4 py-3">${passed ? '<span class="px-3 py-1 text-xs font-semibold text-green-700 bg-green-100 rounded-full">PASSED</span>' : '<span class="px-3 py-1 text-xs font-semibold text-red-700 bg-red-100 rounded-full">FAILED</span>'}</td>
      `;
      tbody.appendChild(tr);
    });
  }

  function applyDashboardFilters(recentGrades) {
    const subj = document.getElementById('dashboardSubject')?.value;
    const student = document.getElementById('dashboardStudent')?.value;
    const cls = document.getElementById('dashboardClass')?.value;
    const filtered = recentGrades.filter(g => {
      if (subj && String(g.subject_id) !== String(subj)) return false;
      if (student && String(g.student_id) !== String(student)) return false;
      if (cls && g.subject_class_year !== cls && g.student_school_year !== cls) return false;
      return true;
    });
    renderRecentGrades(filtered.slice(0, 50));
  }

  document.addEventListener('DOMContentLoaded', () => {
    fetchAndRenderStats();
    const recentGrades = getRecentGrades();
    populateClassOptions(recentGrades);
    renderRecentGrades(recentGrades.slice(0, 10));
    document.getElementById('dashboardApply')?.addEventListener('click', () => applyDashboardFilters(recentGrades));
    document.getElementById('dashboardReset')?.addEventListener('click', () => {
      document.getElementById('dashboardSubject').value = '';
      document.getElementById('dashboardStudent').value = '';
      document.getElementById('dashboardClass').value = '';
      renderRecentGrades(recentGrades.slice(0, 10));
    });
  });
})();
