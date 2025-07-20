export interface DBMessage {
  role: "data" | "system" | "user" | "assistant";
  content: string;
  created_at: number;

}

export interface Message {
  role: "data" | "system" | "user" | "assistant";
  content: any[];
  created_at: number;
}

export interface Account {
  id: number;
  customer_id: number;
  nickname: string;
  number: string;
  balance: number;
  created_at: string;
}

export interface Transaction {
  id: number;
  payee: string;
  amount: number;
  description: string;
  created_at: number;
}