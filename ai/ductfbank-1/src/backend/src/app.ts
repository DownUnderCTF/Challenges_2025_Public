import { Hono } from "hono";
import { router as ai } from './routes/ai';
import { router as dashboard } from './routes/dashboard';
import { router as login } from './routes/login';
import { serveStatic } from "hono/bun";

const app = new Hono();
app.use('/widget/*', serveStatic({
  root: './widget/dist/',
  rewriteRequestPath: (path) =>
    path.replace(/^\/widget/, '/'),
  onNotFound: (path, c) => {
    console.log(`${path} is not found, you access ${c.req.path}`)
  }
}));
app.route('/ai', ai);
app.route('/login', login);
app.route('/', dashboard);

export default app