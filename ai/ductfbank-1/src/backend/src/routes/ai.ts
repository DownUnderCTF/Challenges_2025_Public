import { Hono } from "hono";
import { createConversation, getConversation, listConversations, listMessages, run } from "../agent";
import { jwtAuth } from "../middleware";
import { SECRET } from "../config";
import { HTTPException } from "hono/http-exception";


export const router = new Hono();
router.use("/*", jwtAuth({
  secret: SECRET,
  verifyOptions: {
    algorithms: ['HS256']
  }
}));

router.get('/conversations', async (c) => {
  const customer = c.get('jwtPayload').sub;

  return c.json(await listConversations(customer));
});

router.post('/conversations', async (c) => {
  const customer = c.get('jwtPayload').sub;

  const id = await createConversation(customer);
  return c.json({ id });
});

router.get('/conversations/:id', async (c) => {
  const customer = c.get('jwtPayload').sub;
  await getConversation(+c.req.param().id, customer);
  const messages = await listMessages(+c.req.param().id);
  return c.json(messages.filter(({ role }) => role === 'user' || role === 'assistant')
    .flatMap(({ role, content, created_at }) => {
      const out: { role: string, content: string, created_at: number }[] = [];
      if (Array.isArray(content)) {
        for (const cn of content) {
          if (typeof cn === 'string') {
            out.push({ role, content: cn, created_at });
          } else if (cn && cn.type === 'text' && cn.text) {
            out.push({ role, content: cn.text, created_at });
          }
        }
      } else if (typeof content === 'string') {
        out.push({ role, content, created_at });
      } else if (content && content.type === 'text') {
        out.push({ role, content: content.text, created_at });
      }
      return out;
    }));
});

router.post('/conversations/:id', async (c) => {
  const customer = c.get('jwtPayload').sub;
  const message = (await c.req.json()).message;
  const id = +c.req.param().id;
  if (typeof message !== 'string') throw new HTTPException(400, { message: 'message must be string' });
  if (message.length > 300) throw new HTTPException(400, { message: 'your message is too long' });
  return c.json(await run(id, customer, message));
});