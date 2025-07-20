import { Hono } from 'hono';
import { randomBytes } from "node:crypto";
import { LoginLayout } from './layouts.ts';
import { uniqueNamesGenerator, names, adjectives, animals } from 'unique-names-generator';
import { BankService } from '../bank_service.ts';
import { HTTPException } from 'hono/http-exception';
import { setCookie } from 'hono/cookie';
import { sign } from 'jsonwebtoken';
import { SECRET } from '../config.ts';

const svc = BankService.getInstance();

export const router = new Hono();
router.get('/', (c) => c.html(LoginLayout({
  title: 'Login',
  body: `
  <div class="container">
    <div class="details-container">
      <h2 class="text-center mb-4">Login</h2>
      <form action="/login" method="POST">
        <div class="form-group">
          <label for="loginField">Username</label>
          <input type="text" class="form-control" name="login" placeholder="Enter username" required>
        </div>
        <div class="form-group">
          <label for="passwordField">Password</label>
          <input type="password" class="form-control" name="password" placeholder="Enter password" required>
        </div>
        <button type="submit" class="btn btn-primary mt-3">Login</button>
      </form>

      <div class="text-center mt-3">
        <small>Don't have an account?</small>
        <form action="/login/new" method="POST">
          <button class="btn btn-success" action="submit">Register</button>
        </form>
      </div>
    </div>
  </div>
  `
})));

router.post('/', async (c) => {
  const { login, password } = await c.req.parseBody();
  if (typeof login !== 'string' || typeof password !== 'string') {
    throw new HTTPException(401, { message: "Login and password must be strings" });
  }
  const id = await svc.authenticate(login, password);
  setCookie(c, 'bank-session', sign({ sub: id }, SECRET), {
    httpOnly: true,
  });
  return c.redirect('/');
});


router.post('/new', async (c) => {
  const name = uniqueNamesGenerator({ dictionaries: [names, names], length: 2 }).replace('_', ' ');
  const login = uniqueNamesGenerator({ dictionaries: [adjectives, animals], length: 2 });
  const password = randomBytes(10).toString('hex');
  await svc.createCustomer(name, login, password);
  return c.html(LoginLayout({
    title: 'New User',
    body: `
  <div class="container">
    <div class="details-container">
      <form method="POST" action="/login">
        <h2 class="text-center mb-4">Registration Details</h2>
        <p>Please make a copy of these details! They will only be shown once.</p>
        <div class="card">
          <div class="card-body">
    
            <div class="form-group">
              <label>Name</label>
              <input type="text" class="form-control" name="name" value="${name}" disabled>
            </div>
            
            <div class="form-group">
              <label>Username</label>
              <input type="text" class="form-control" name="login" value="${login}" readonly>
            </div>
            <div class="form-group">
              <label>Password</label>
              <input type="text" class="form-control" name="password" value="${password}" readonly>
            </div>
          </div>
        </div>
        
        <div class="text-center mt-4">
          <input type="submit" class="btn btn-primary" value="Login" />
        </div>
      </form>
    </div>
  </div>
    
  `
  }))
});