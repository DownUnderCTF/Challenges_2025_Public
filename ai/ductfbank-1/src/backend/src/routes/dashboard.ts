import { Hono } from "hono";
import { jwtAuth } from "../middleware";
import { SECRET } from "../config";
import { DashboardLayout } from "./layouts";
import { BankService } from "../bank_service";
import { Account, Transaction } from "../types";
import { HTTPException } from "hono/http-exception";
import { deleteCookie } from "hono/cookie";

export const router = new Hono();
const svc = BankService.getInstance();

router.use("/*", jwtAuth({
  secret: SECRET,
  verifyOptions: {
    algorithms: ['HS256']
  }
}));

const AccountFragment = (props: Account) => `
<a href="/accounts/${props.number}" class="text-decoration-none">
  <div class="account-card card mb-3">
    <div class="card-body">
      <div class="row align-items-center">
        <div class="col-auto">
          <div class="bg-primary text-white rounded-circle p-3">
            <i class="fas fa-university"></i>
          </div>
        </div>
        <div class="col">
          <h5 class="mb-1">${props.nickname}</h5>
          <div class="account-id mb-1">Account Number: ${props.number}</div>
        </div>
        <div class="col-auto">
          <div class="account-balance text-success">$${props.balance.toFixed(2)}</div>
        </div>
      </div>
    </div>
  </div>
</a>
`;

const TransactionFragment = (props: Transaction) => `
  <tr class="transaction-row">
    <td class="font-weight-bold">${props.payee}</td>
    <td>${new Date(props.created_at)}</td>
    <td>${props.description}</td>
    <td class="text-right font-weight-bold transaction-amount-${props.amount >= 0 ? 'positive' : 'negative'}">
      ${props.amount >= 0 ? '+' : '-'}$${Math.abs(props.amount).toFixed(2)}
    </td>
  </tr>
`;

router.get('/', async (c) => {
  const accounts = await svc.listAccounts(c.get('jwtPayload').sub);
  return c.html(DashboardLayout({
    title: 'Accounts',
    body: `
  <!-- Dashboard Header -->
        <div class="dashboard-header py-3">
          <div class="row align-items-center">
            <div class="col">
              <h1 class="h3">Account Overview</h1>
              <p class="text-muted">View and manage your bank accounts</p>
            </div>
            <div class="col-auto">
              <div class="btn-group">
                <button type="button" class="btn btn-outline-primary" disabled>
                  <i class="fas fa-plus mr-1"></i> New Account (not available)
                </button>
              </div>
            </div>
          </div>
        </div>

        <!-- Accounts List -->
        <div class="card shadow mb-4">
          <div class="card-body">
            ${accounts.map((acc) => AccountFragment(acc)).join('')}
          </div>
        </div>
    `
  }));
});

router.get('/logout', async (c) => {
  deleteCookie(c, 'bank-session');
  return c.redirect('/login');
});

router.post('/accounts/:number', async (c) => {
  const customer = c.get('jwtPayload').sub;
  // validate number
  const number = c.req.param().number.replace(/[^0-9]/g, '');
  const account = await svc.getAccount(number);
  if (account.customer_id !== customer) {
    throw new HTTPException(403, { message: 'You don\'t have access to this account' });
  }
  const { nickname } = await c.req.parseBody();
  if (typeof nickname !== 'string') {
    throw new HTTPException(400, { message: 'nickname is invalid' });
  }
  if (nickname.length > 128) {
    throw new HTTPException(400, { message: 'nickname is too long' });

  }
  await svc.updateNickname(account.id, nickname);
  return c.redirect('/accounts/' + number);
});

router.get('/accounts/:number', async (c) => {
  const customer = c.get('jwtPayload').sub;
  // validate number
  const number = c.req.param().number.replace(/[^0-9]/g, '');
  const account = await svc.getAccount(number);
  if (account.customer_id !== customer) {
    throw new HTTPException(403, { message: 'You don\'t have access to this account' });
  }
  const transactions = await svc.listTransactions(account.id);
  return c.html(DashboardLayout({
    title: 'Transactions',
    body: `
        <!-- Dashboard Header -->
        <div class="dashboard-header py-3">
          <nav aria-label="breadcrumb">
            <ol class="breadcrumb bg-transparent p-0">
              <li class="breadcrumb-item"><a href="/">Dashboard</a></li>
              <li class="breadcrumb-item active" aria-current="page">Account Transactions</li>
            </ol>
          </nav>
          <div class="row align-items-center">
            <div class="col">
              <h1 class="h3 mb-0" id="account-name">${account.nickname}</h1>
              <form method="POST">
                <input name="nickname" class="form-control" value="${account.nickname}"/>
                <input type="submit" class="btn btn-info" value="Update Nickname"/>
              </form>
              <p class="text-muted mb-0" id="account-id">Account Number: ${account.number}</p>
            </div>
          </div>
        </div>

        <!-- Account Overview -->
        <div class="row my-4">
          <div class="col-12 col-md-4">
            <div class="card mb-4">
              <div class="card-body">
                <h6 class="text-muted mb-1">Current Balance</h6>
                <h3 class="text-success mb-0" id="current-balance">$${account.balance.toFixed(2)}</h3>
              </div>
            </div>
          </div>
        </div>

        <!-- Transactions Table -->
        <div class="card shadow mb-4">
          <div class="card-header py-3 d-flex flex-row align-items-center justify-content-between">
            <h6 class="m-0 font-weight-bold text-primary">Transactions</h6>
          </div>
          <div class="card-body p-0">
            <div class="table-responsive">
              <table class="table mb-0">
                <thead class="bg-light">
                  <tr>
                    <th scope="col">Payee</th>
                    <th scope="col">Date Created</th>
                    <th scope="col">Description</th>
                    <th scope="col" class="text-right">Amount</th>
                  </tr>
                </thead>
                <tbody>
                  ${transactions.map((tx) => TransactionFragment(tx)).join('')}

                </tbody>
              </table>
            </div>
          </div>

    `
  }));
});

