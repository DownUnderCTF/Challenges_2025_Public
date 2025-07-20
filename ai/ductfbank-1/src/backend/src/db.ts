import Database from "bun:sqlite";
import { mkdir } from "node:fs/promises";
import { FLAG_SQLI } from "./config";

await mkdir("data", { recursive: true });

export const Conversations = new Database("data/conversations.db");
await Conversations.exec(`
  -- Create conversations table
  CREATE TABLE IF NOT EXISTS conversations (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    customer_id INTEGER NOT NULL,
    summary TEXT,
    created_at INTEGER DEFAULT(CAST((unixepoch('now','subsec')*1000) as integer))
  );

  -- Create messages table with an index on conversation_id
  CREATE TABLE IF NOT EXISTS messages (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    conversation_id INTEGER NOT NULL,
    role TEXT NOT NULL,
    content TEXT NOT NULL,
    created_at INTEGER DEFAULT(CAST((unixepoch('now','subsec')*1000) as integer)),
    FOREIGN KEY (conversation_id) REFERENCES conversations(id)
  );

  -- Create an index on conversation_id for faster queries
  CREATE INDEX IF NOT EXISTS idx_messages_conversation_id ON messages(conversation_id);
`);

export const Bank = new Database("data/bank.db");
await Bank.exec(`
  -- Create customers table
  CREATE TABLE IF NOT EXISTS customers (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    name TEXT NOT NULL,
    login TEXT NOT NULL UNIQUE,
    password TEXT NOT NULL,
    created_at INTEGER DEFAULT(CAST((unixepoch('now','subsec')*1000) as integer))
  );

  -- Create accounts table
  CREATE TABLE IF NOT EXISTS accounts (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    customer_id INTEGER NOT NULL,
    nickname TEXT NOT NULL,
    number TEXT NOT NULL UNIQUE,
    balance DECIMAL(10, 2) NOT NULL DEFAULT 0.00,
    created_at INTEGER DEFAULT(CAST((unixepoch('now','subsec')*1000) as integer)),
    FOREIGN KEY (customer_id) REFERENCES customers(id)
  );

  -- Create transactions table
  CREATE TABLE IF NOT EXISTS transactions (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    account_id INTEGER NOT NULL,
    payee TEXT NOT NULL,
    amount DECIMAL(10, 2) NOT NULL,
    description TEXT,
    created_at INTEGER DEFAULT(CAST((unixepoch('now','subsec')*1000) as integer)),
    FOREIGN KEY (account_id) REFERENCES accounts(id)
  );

  -- Create flag table
  CREATE TABLE IF NOT EXISTS flags (
    flag TEXT NOT NULL UNIQUE
  );

  -- Create indexes for faster querying
  CREATE INDEX IF NOT EXISTS idx_accounts_customer_id ON accounts(customer_id);
  CREATE INDEX IF NOT EXISTS idx_transactions_account_id ON transactions(account_id);

  INSERT INTO flags (flag) VALUES ('${FLAG_SQLI}') ON CONFLICT (flag) DO NOTHING;
`);
