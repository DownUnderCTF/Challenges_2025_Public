import { html, raw } from 'hono/html';
interface SiteData {
  title: string,
  head?: string | Promise<string>,
  body?: string | Promise<string>
}

export const BaseLayout = (props: SiteData) => html`
<!DOCTYPE html>
<html lang="en">
<head>
  <meta charset="UTF-8">
  <meta name="viewport" content="width=device-width, initial-scale=1.0">
  <title>DownUnderCTF Bank - ${props.title}</title>
  <!-- Bootstrap 4 CSS -->
  <link rel="stylesheet" href="https://cdnjs.cloudflare.com/ajax/libs/twitter-bootstrap/4.6.0/css/bootstrap.min.css">
  ${raw(props.head)}
</head>
<body>
  ${raw(props.body)}

  <!-- Bootstrap JS and dependencies -->
  <script src="https://cdnjs.cloudflare.com/ajax/libs/jquery/3.5.1/jquery.slim.min.js"></script>
  <script src="https://cdnjs.cloudflare.com/ajax/libs/popper.js/1.16.1/umd/popper.min.js"></script>
  <script src="https://cdnjs.cloudflare.com/ajax/libs/twitter-bootstrap/4.6.0/js/bootstrap.min.js"></script>
</body>
</html>
`

export const LoginLayout = (props: SiteData) => BaseLayout({
  title: props.title,
  head: html`
    <style>
      .details-container {
        max-width: 400px;
        margin: 100px auto;
        padding: 20px;
        border-radius: 5px;
        box-shadow: 0 0 10px rgba(0, 0, 0, 0.1);
      }
      .btn {
        width: 100%;
      }

      .detail-row {
        padding: 10px 0;
        border-bottom: 1px solid #eee;
      }
      .detail-row:last-child {
        border-bottom: none;
      }
    </style>
  `,
  body: props.body
})

export const DashboardLayout = (props: SiteData) => BaseLayout({
  title: props.title,
  head: `
  <style>
    .sidebar {
      min-height: 100vh;
      background-color: #343a40;
      color: #fff;
    }
    .sidebar-sticky {
      position: -webkit-sticky;
      position: sticky;
      top: 0;
      height: calc(100vh - 48px);
      padding-top: 1rem;
      overflow-x: hidden;
      overflow-y: auto;
    }
    .sidebar .nav-link {
      font-weight: 500;
      color: rgba(255, 255, 255, 0.75);
    }
    .sidebar .nav-link:hover {
      color: #fff;
    }
    .sidebar .nav-link.active {
      color: #fff;
    }
    .account-card {
      border-left: 4px solid #007bff;
      transition: all 0.3s ease;
    }
    .account-card:hover {
      transform: translateY(-5px);
      box-shadow: 0 4px 8px rgba(0, 0, 0, 0.1);
    }
    .account-balance {
      font-size: 1.5rem;
      font-weight: bold;
    }
    .account-id {
      opacity: 0.6;
      font-size: 0.8rem;
    }
    .dashboard-header {
      background-color: #f8f9fa;
      border-bottom: 1px solid #e3e6f0;
    }
    .transaction-row:hover {
      background-color: rgba(0, 123, 255, 0.05);
    }
    .transaction-type {
      width: 40px;
      height: 40px;
      display: flex;
      align-items: center;
      justify-content: center;
    }
    .transaction-status-pending {
      font-size: 0.75rem;
      padding: 0.15rem 0.5rem;
      border-radius: 2rem;
      background-color: #ffeeba;
      color: #856404;
    }
    .transaction-status-completed {
      font-size: 0.75rem;
      padding: 0.15rem 0.5rem;
      border-radius: 2rem;
      background-color: #d4edda;
      color: #155724;
    }
    .transaction-status-declined {
      font-size: 0.75rem;
      padding: 0.15rem 0.5rem;
      border-radius: 2rem;
      background-color: #f8d7da;
      color: #721c24;
    }
    .transaction-amount-positive {
      color: #28a745;
    }
    .transaction-amount-negative {
      color: #dc3545;
    }
    .filter-controls {
      background-color: #f8f9fa;
      border-radius: 0.25rem;
    }
  </style>
  ${props.head || ''}
  `,
  body: `
  <div class="container-fluid">
    <div class="row">
      <!-- Sidebar -->
      <nav class="col-md-2 d-none d-md-block sidebar">
        <div class="sidebar-sticky">
          <div class="text-center my-4">
            <h5>DownUnderCTF Bank</h5>
          </div>
          <ul class="nav flex-column">
            <li class="nav-item">
              <a class="nav-link active" href="/">
                Dashboard
              </a>
            </li>
            <li class="nav-item">
              <a class="nav-link" href="/logout">
                Logout
              </a>
            </li>
          </ul>
        </div>
      </nav>

      <!-- Main content -->
      <main role="main" class="col-md-10 ml-sm-auto px-4">
        ${props.body}
        <iframe src="/widget/index.html" scrolling="no" style=" width: 600px; height: 600px; border: 0; position: fixed; right: 0; bottom: 30px"></iframe>

      </main>
    </div>
  </div>
  `
});
