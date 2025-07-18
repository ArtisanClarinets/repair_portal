<!-- File: client_portal/LayoutShell.vue -->
<!-- Last Updated: 2025-07-16 -->
<template>
  <div class="wrapper">
    <!-- Top Navbar -->
    <nav class="main-header navbar navbar-expand navbar-white navbar-light">
      <ul class="navbar-nav">
        <li class="nav-item">
          <a class="nav-link" data-widget="pushmenu" href="#"><i class="fas fa-bars"></i></a>
        </li>
        <li class="nav-item d-none d-sm-inline-block">
          <a href="/" class="nav-link">Home</a>
        </li>
      </ul>
    </nav>

    <!-- Sidebar -->
    <aside class="main-sidebar sidebar-dark-primary elevation-4">
      <a href="#" class="brand-link">
        <img src="/public/adminlte/img/AdminLTELogo.png" alt="Logo" class="brand-image img-circle elevation-3" style="opacity: .8">
        <span class="brand-text font-weight-light">Repair Portal</span>
      </a>

      <div class="sidebar">
        <nav class="mt-2">
          <ul class="nav nav-pills nav-sidebar flex-column" data-widget="treeview" role="menu">
            <li class="nav-item">
              <a href="?view=client_profile" class="nav-link">
                <i class="nav-icon fas fa-user"></i>
                <p>Client Profile</p>
              </a>
            </li>
          </ul>
        </nav>
      </div>
    </aside>

    <!-- Page Content -->
    <div class="content-wrapper p-3">
      <slot></slot>
    </div>
  </div>
</template>

<script>
export default {
  name: "LayoutShell"
};
</script>

