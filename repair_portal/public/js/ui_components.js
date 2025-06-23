# --- File: apps/repair_portal/public/js/ui_components.js ---
// Updated: 2025-07-12
// Version: 1.0
// Purpose: Reusable UI helpers for The Clarinet Wizard portal.

function toggleMobileNav() {
  const menu = document.getElementById('navMenu');
  if (menu) {
    menu.classList.toggle('show');
  }
}

function showToast(message, duration = 3000) {
  const toast = document.createElement('div');
  toast.className = 'toast-message bg-accent rounded p-2';
  toast.textContent = message;
  document.body.appendChild(toast);
  setTimeout(() => toast.remove(), duration);
}

function openModal(id) {
  document.getElementById(id)?.classList.add('show');
}

function closeModal(id) {
  document.getElementById(id)?.classList.remove('show');
}
