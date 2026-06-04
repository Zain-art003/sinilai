// SiNilai — SMA XYZ | Main JS

// ===== DATE/TIME =====
function updateDate() {
    const el = document.getElementById('topbar-date');
    if (!el) return;
    const now = new Date();
    const opts = { weekday: 'long', year: 'numeric', month: 'long', day: 'numeric' };
    el.textContent = now.toLocaleDateString('id-ID', opts);
}
updateDate();

// ===== SIDEBAR TOGGLE =====
function toggleSidebar() {
    const sidebar = document.getElementById('sidebar');
    if (sidebar) sidebar.classList.toggle('open');
}

// Close sidebar when clicking outside on mobile
document.addEventListener('click', function(e) {
    const sidebar = document.getElementById('sidebar');
    const toggle = document.querySelector('.sidebar-toggle');
    if (sidebar && sidebar.classList.contains('open')) {
        if (!sidebar.contains(e.target) && e.target !== toggle && !toggle?.contains(e.target)) {
            sidebar.classList.remove('open');
        }
    }
});

// ===== CONFIRM DELETE MODAL =====
let pendingForm = null;

function confirmDelete(message) {
    const modal = document.getElementById('delete-modal');
    const msgEl = document.getElementById('delete-message');
    if (modal) {
        if (msgEl) msgEl.textContent = message || 'Apakah Anda yakin ingin menghapus data ini?';
        modal.classList.add('active');
    }
}

function closeModal() {
    const modal = document.getElementById('delete-modal');
    if (modal) modal.classList.remove('active');
    pendingForm = null;
}

function setupDeleteForms() {
    document.querySelectorAll('.delete-form').forEach(form => {
        form.addEventListener('submit', function(e) {
            e.preventDefault();
            pendingForm = this;
            const msg = this.dataset.message;
            confirmDelete(msg);
        });
    });

    const confirmBtn = document.getElementById('confirm-delete');
    if (confirmBtn) {
        confirmBtn.addEventListener('click', function() {
            if (pendingForm) {
                pendingForm.submit();
            }
            closeModal();
        });
    }
}

// ===== NILAI CALCULATOR (Real-time) =====
function setupNilaiCalculator() {
    const tugasInput = document.getElementById('nilai_tugas');
    const utsInput   = document.getElementById('nilai_uts');
    const uasInput   = document.getElementById('nilai_uas');
    const naDisplay  = document.getElementById('calc-na');
    const statusDisplay = document.getElementById('calc-status');

    if (!tugasInput || !utsInput || !uasInput) return;

    function calculate() {
        const t   = parseFloat(tugasInput.value) || 0;
        const uts = parseFloat(utsInput.value)   || 0;
        const uas = parseFloat(uasInput.value)    || 0;

        // Validate range
        if ([t, uts, uas].some(v => v < 0 || v > 100)) return;

        const na = (0.30 * t) + (0.30 * uts) + (0.40 * uas);
        const naRounded = Math.round(na * 100) / 100;
        const status = naRounded >= 70 ? 'LULUS' : 'TIDAK LULUS';

        if (naDisplay) {
            naDisplay.textContent = naRounded.toFixed(2);
            naDisplay.className = 'calc-num ' + (naRounded >= 70 ? 'score-high' : 'score-low');
        }
        if (statusDisplay) {
            statusDisplay.textContent = status;
            statusDisplay.className = 'badge ' + (naRounded >= 70 ? 'badge-lulus' : 'badge-tidak-lulus');
        }
    }

    [tugasInput, utsInput, uasInput].forEach(el => {
        el.addEventListener('input', calculate);
    });

    calculate();
}

// ===== DEMO ACCOUNT AUTOFILL =====
function setupDemoAccounts() {
    document.querySelectorAll('.demo-account').forEach(btn => {
        btn.addEventListener('click', function() {
            const u = this.dataset.user;
            const p = this.dataset.pass;
            const uField = document.getElementById('username');
            const pField = document.getElementById('password');
            if (uField) uField.value = u;
            if (pField) pField.value = p;

            // Animate
            if (uField) uField.focus();
        });
    });
}

// ===== SCORE COLOR UTIL =====
function applyScoreColors() {
    document.querySelectorAll('.auto-score').forEach(el => {
        const val = parseFloat(el.textContent);
        if (val >= 80) el.classList.add('score-high');
        else if (val >= 70) el.classList.add('score-mid');
        else el.classList.add('score-low');
    });

    document.querySelectorAll('.auto-progress').forEach(el => {
        const val = parseFloat(el.dataset.val);
        const fill = el.querySelector('.progress-fill');
        if (fill) {
            fill.style.width = Math.min(val, 100) + '%';
            if (val >= 80) fill.classList.add('high');
            else if (val >= 70) fill.classList.add('mid');
            else fill.classList.add('low');
        }
    });
}

// ===== INIT =====
document.addEventListener('DOMContentLoaded', function() {
    setupDeleteForms();
    setupNilaiCalculator();
    setupDemoAccounts();
    applyScoreColors();

    // Auto-hide alerts after 5s
    document.querySelectorAll('.alert').forEach(el => {
        setTimeout(() => {
            el.style.transition = 'opacity 0.5s';
            el.style.opacity = '0';
            setTimeout(() => el.remove(), 500);
        }, 5000);
    });
});
