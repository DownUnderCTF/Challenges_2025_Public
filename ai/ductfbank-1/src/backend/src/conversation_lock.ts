export class ConversationLockTable {
  private static instance: ConversationLockTable;
  private lockedConversations: Set<number>;

  private constructor() {
    this.lockedConversations = new Set<number>();
  }

  /**
   * Get the singleton instance of the lock table
   */
  public static getInstance(): ConversationLockTable {
    if (!ConversationLockTable.instance) {
      ConversationLockTable.instance = new ConversationLockTable();
    }
    return ConversationLockTable.instance;
  }

  /**
   * Attempt to acquire a lock for a conversation ID
   * @param conversationId The conversation ID to lock
   * @throws Error if the conversation is already locked
   */
  public acquire(conversationId: number) {
    const self = this;
    if (this.lockedConversations.has(conversationId)) {
      throw new Error(`Conversation ${conversationId} is already locked`);
    }
    
    this.lockedConversations.add(conversationId);
    return {
      [Symbol.dispose]() {
        self.release(conversationId);
      }
    }
  }

  /**
   * Release a lock for a conversation ID
   * @param conversationId The conversation ID to unlock
   * @throws Error if the conversation wasn't locked
   */
  private release(conversationId: number): void {
    if (!this.lockedConversations.has(conversationId)) {
      throw new Error(`Conversation ${conversationId} is not locked`);
    }
    
    this.lockedConversations.delete(conversationId);
  }

  /**
   * Check if a conversation is currently locked
   * @param conversationId The conversation ID to check
   * @returns true if the conversation is locked, false otherwise
   */
  public isLocked(conversationId: number): boolean {
    return this.lockedConversations.has(conversationId);
  }

  /**
   * Get all currently locked conversation IDs
   * @returns Array of locked conversation IDs
   */
  public getAllLocks(): number[] {
    return Array.from(this.lockedConversations);
  }

  /**
   * Get the number of currently locked conversations
   * @returns Count of locked conversations
   */
  public getLocksCount(): number {
    return this.lockedConversations.size;
  }

  /**
   * Reset all locks (use with caution)
   */
  public reset(): void {
    this.lockedConversations.clear();
  }
}