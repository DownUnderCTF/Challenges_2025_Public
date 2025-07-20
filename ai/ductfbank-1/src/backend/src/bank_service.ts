import Database from "bun:sqlite";
import { HTTPException } from 'hono/http-exception';
import { FLAG_BONUS } from "./config";
import { Bank } from "./db";
import { Account, Transaction } from "./types";

export class BankService {
  constructor(private readonly db: Database) { }

  async createCustomer(name: string, login: string, password: string) {
    const query = this.db.query('INSERT INTO customers (name, login, password) VALUES (?, ?, ?)');
    await query.run(name, login.toLocaleLowerCase(), password);
  }

  async authenticate(login: string, password: string): Promise<number> {
    const query = this.db.query('SELECT id FROM customers WHERE login=? and password=?');
    const result = await query.get(login.toLocaleLowerCase(), password) as { id: number };
    if (!result) throw new HTTPException(401, { message: "Invalid login or password" });
    return result.id;
  }

  async getAccount(number: string): Promise<Account> {
    const stmt = this.db.query(`
      SELECT id, customer_id, number, nickname, balance, created_at
      FROM accounts
      WHERE number='${number}'
    `);
    const result = await stmt.get();
    if (!result) throw new HTTPException(404, { message: "Account does not exist" });
    return result;
  }

  async listAccounts(customerId: number): Promise<Account[]> {
    const stmt = this.db.query(`
      SELECT id, customer_id, number, nickname, balance, created_at
      FROM accounts
      WHERE customer_id=${customerId}
    `);
    return await stmt.all();
  }

  async updateNickname(accountId: number, nickname: string): Promise<void> {
    const stmt = this.db.query(`
      UPDATE accounts SET nickname=? WHERE id=?
    `);
    return await stmt.run(nickname, accountId);
  }

  async listTransactions(accountId: number): Promise<Transaction[]> {
    const stmt = this.db.query(`
      SELECT id, payee, amount, description, created_at
      FROM transactions
      WHERE account_id=${accountId}
      ORDER BY id DESC
    `);
    return await stmt.all();
  }


  async createAccount(customerId: number, nickname: string): Promise<string> {
    const account = Math.floor(Math.random() * 10000000000).toString().padStart(9, '0');
    const stmt = this.db.query(
      'INSERT INTO accounts (customer_id, number, nickname) VALUES (?, ?, ?)'
    );
    await stmt.run(customerId, account, nickname);
    return account;
  }

  async giveBonus(account: string) {
    return this.db.transaction(async () => {
      const { id } = await this.db.query('SELECT id FROM accounts WHERE number=?').get(account) as { id: number };
      await this.addTransaction(id, 'DUCTF Bank', `Account opening bonus: ${FLAG_BONUS}`, 1000);
    })();
  }

  async createTransaction(sourceAccount: string, destinationAccount: string, description: string, amount: number) {
    if (amount <= 0) throw new Error("Amount cannot be negative");
    return this.db.transaction(async () => {
      const getAccount = this.db.query('SELECT id, balance FROM accounts WHERE number=?');
      const src = await getAccount.get(sourceAccount) as { id: number, balance: number };
      const dst = await getAccount.get(destinationAccount) as { id: number, balance: number };
      if (!src) {
        throw new Error("Source account does not exist");
      }
      if (!dst) {
        throw new Error("Destination account does not exsit");
      }
      if (src.balance - amount < 0) {
        throw new Error("Balance after transacting cannot be below zero");
      }
      await this.addTransaction(src.id, destinationAccount, description, -amount);
      await this.addTransaction(dst.id, sourceAccount, description, amount);
    })();
  }

  private async addTransaction(accountId: number, payee: string, description: string, amount: number) {
    const txInsert = this.db.query(
      'INSERT INTO transactions (account_id, payee, description, amount) VALUES (?,?,?,?)'
    );
    const balUpdate = this.db.query('UPDATE accounts SET balance=balance+? WHERE id=?');
    await txInsert.run(accountId, payee, description, amount);
    await balUpdate.run(amount, accountId);
  }

  public static getInstance() {
    return new BankService(Bank);
  }
}