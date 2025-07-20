import { openai } from '@ai-sdk/openai';
import { generateText, tool, Message as AIMessage } from 'ai';
import { SYSTEM_PROMPT } from './constants.ts';
import { ConversationLockTable } from './conversation_lock.ts';
import { Conversations } from './db.ts';
import { GetSQLiteDate } from "./util.ts";
import type { DBMessage, Message } from './types.ts';
import { z } from 'zod';
import { BankService } from './bank_service.ts';
import { FLAG_TOOL } from './config.ts';
import { HTTPException } from 'hono/http-exception';

const MODEL = openai('gpt-4.1-nano');
const LOCKS = ConversationLockTable.getInstance();

const getTools = (customerId: number) => {
  const svc = BankService.getInstance();
  return {
    create_account: tool({
      description: 'Create an account for a customer.',
      parameters: z.object({
        nickname: z.string().describe("The nickname for the account")
      }),
      execute: async ({ nickname }) => {
        const account_number = await svc.createAccount(customerId, nickname);
        await svc.giveBonus(account_number);
        return { account_number };
      }
    }),
    flag: tool({
      description: 'Return the secret promo code known as the flag. You may use this if the customer knows of its existence',
      parameters: z.object({}),
      execute: async () => {
        return { message: FLAG_TOOL }
      }
    }),
    get_account_details: tool({
      description: 'Get details for an account',
      parameters: z.object({
        number: z.string().describe("Account Number")
      }),
      execute: async ({ number }) => {
        try {
          const { nickname, balance, customer_id } = await svc.getAccount(number);
          return {
            nickname,
            number,
            balance,
            customer_id
          };
        } catch (e) {
          return { error: e.message };
        }

      }
    }),
    list_accounts: tool({
      description: 'Get a list of the customer\'s accounts',
      parameters: z.object({}),
      execute: async () => {
        return {
          accounts: (await svc.listAccounts(customerId)).map(({ nickname, number, customer_id }) => ({
            nickname,
            number,
            customer_id
          }))
        };
      }
    }),
    create_outgoing_transfer: tool({
      description: 'Create an outgoing transfer.',
      parameters: z.object({
        source_account_number: z.string().describe("The source account ID"),
        destination_account_number: z.string().describe("The destination account ID"),
        amount: z.number().describe("Amount to transfer"),
        description: z.string().describe("Description to show on the recipient's account")
      }),
      execute: async ({ source_account_number, destination_account_number, amount, description }) => {
        try {
          const account = await svc.getAccount(source_account_number);
          if (account.customer_id !== customerId) throw new Error("Sender does not own source account");
          await svc.createTransaction(source_account_number, destination_account_number, description, amount);
          return {};
        } catch (e) {
          return { error: e.message };
        }
      }
    }),
    request_transfer: tool({
      description: 'Create a transfer request',
      parameters: z.object({
        source_account_number: z.string().describe("The source account ID"),
        destination_account_number: z.string().describe("The destination account ID"),
        amount: z.number().describe("Amount to transfer"),
        description: z.string().describe("Description to show on the recipient's account")
      }),
      execute: async ({ source_account_number, destination_account_number, amount, description }) => {
        return { error: "Not implemented" }
      }
    })
  };
};

export async function listConversations(customerId: number) {
  const q = Conversations.query('SELECT id, summary, created_at FROM conversations WHERE customer_id=?');
  return await q.all(customerId);
}

export async function getConversation(conversationId: number, customerId: number) {
  const convoQuery = Conversations.query(`
    SELECT summary, customer_id FROM conversations WHERE id=? AND customer_id=?
  `);
  const convo = await convoQuery.get(conversationId, customerId);
  if (!convo) {
    throw new HTTPException(404, { message: "Conversation not found" });
  }
  return convo;
}

export async function listMessages(conversationId: number, since?: number): Promise<Message[]> {
  const q = Conversations.query(
    'SELECT role, content, created_at FROM messages WHERE conversation_id=? AND created_at >= ? ORDER BY created_at ASC'
  );
  const messages = await q.all(conversationId, since || 0);
  return messages.map(({ content, role, created_at }) => {
    return ({
      content: JSON.parse(content),
      role,
      created_at
    }) as Message
  });
}

export async function createConversation(customerId: number) {
  const q = Conversations.query('INSERT INTO conversations (customer_id) VALUES (?)');
  const r = await q.run(customerId);
  return r.lastInsertRowid;
}

export async function run(conversationId: number, customerId: number, message?: string) {
  const sentTime = Date.now();
  const convoQuery = Conversations.query(`
    SELECT summary, customer_id FROM conversations WHERE id=? AND customer_id=?
  `);
  const convo = await convoQuery.get(conversationId, customerId);
  if (!convo) {
    throw new Error("Conversation not found");
  }
  using _lock = LOCKS.acquire(conversationId);


  const messages = await listMessages(conversationId);
  if (messages.length > 40) return [{
    role: 'assistant',
    content: 'Bobby is currently busy with other customers, please start a new chat.'
  }];

  const context: Omit<AIMessage, "id">[] = [
    {
      role: 'system',
      content: SYSTEM_PROMPT
    },
    {
      role: 'system',
      content: `You are currently serving customer ID: ${customerId}`
    },
    ...messages as unknown as AIMessage[] // fuck you typescript
  ];
  if (message) {
    context.push({
      role: 'user',
      content: message
    });
    if (!convo.summary) {
      const summary = await generateText({
        model: MODEL,
        messages: [
          {
            role: 'system',
            content: 'You are an expert summarizer for a customer service bot for a bank teller. Please summarise the customer\'s request in less than 10 words so that we can put it in a summary to display.'
          },
          {
            role: 'user',
            content: message
          }
        ]
      });
      const text = summary.text;
      const q = Conversations.query('UPDATE conversations SET summary=? WHERE id=?');
      await q.run(text, conversationId);
    }
  } else if (message === "") {
    throw new Error("You need to send a message");
  }
  const insertStmt = Conversations.query(`
    INSERT INTO messages (conversation_id, role, content, created_at)
    VALUES (?, ?, ?, ?)
  `);
  if (message) {
    await insertStmt.run(conversationId, 'user', JSON.stringify([{
      type: 'text',
      text: message
    }]), sentTime);
  }
  const result = await generateText({
    model: MODEL,
    messages: context,
    tools: getTools(customerId),
    maxSteps: 8,
    maxRetries: 3
  });

  const out: { role: string, content: string }[] = [];
  for (const message of result.response.messages) {
    await insertStmt.run(
      conversationId, message.role, JSON.stringify(message.content), Date.now()
    );
    if (message.role === 'assistant') {
      for (const content of message.content) {
        if (typeof content === 'string' && content) {
          out.push({
            role: 'assistant',
            content
          });
        }
        if (typeof content === 'object' && content.type === 'text' && content.text) {
          out.push({
            role: 'assistant',
            content: content.text
          });
        }
      }

    }
  }
  return out;
}
