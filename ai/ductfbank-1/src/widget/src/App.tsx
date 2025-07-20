import React, { useState, useEffect, useRef } from 'react';
import { MessageSquare, Send, Plus, ArrowLeft, MoreVertical, Loader2, ChevronUp, ChevronDown, X } from 'lucide-react';

// Simple function to parse basic markdown
const parseMarkdown = (text) => {
  if (!text) return '';

  let parsed = text;

  // Handle headings
  parsed = parsed.replace(/^### (.*$)/gm, '<h3>$1</h3>');
  parsed = parsed.replace(/^## (.*$)/gm, '<h2>$1</h2>');
  parsed = parsed.replace(/^# (.*$)/gm, '<h1>$1</h1>');

  // Handle bold
  parsed = parsed.replace(/\*\*(.*?)\*\*/g, '<strong>$1</strong>');

  // Handle italic
  parsed = parsed.replace(/\*(.*?)\*/g, '<em>$1</em>');

  // Handle unordered lists
  parsed = parsed.replace(/^\s*-\s+(.*$)/gm, '<li>$1</li>');

  // Handle ordered lists
  parsed = parsed.replace(/^\s*(\d+)\.\s+(.*$)/gm, '<li>$2</li>');

  // Wrap list items in ul or ol tags
  // This is a simplified approach and might not handle nested lists correctly
  const hasUnorderedList = /(<li>.*<\/li>)/s.test(parsed);
  if (hasUnorderedList) {
    parsed = parsed.replace(/(<li>.*?<\/li>(\s*<li>.*?<\/li>)*)/s, '<ul>$1</ul>');
  }

  // Handle paragraphs - wrap text that's not already in tags
  parsed = parsed.replace(/^(?!<[holup])(.*$)/gm, '<p>$1</p>');

  return parsed;
};

// Component to render markdown content
const MarkdownContent = ({ content }) => {
  return <div dangerouslySetInnerHTML={{ __html: parseMarkdown(content) }} />;
};

const ChatWidget = () => {
  const [view, setView] = useState('selection'); // 'selection' or 'chat'
  const [chats, setChats] = useState([]);
  const [activeChatId, setActiveChatId] = useState(null);
  const [messages, setMessages] = useState([]);
  const [inputMessage, setInputMessage] = useState('');
  const [status, setStatus] = useState('idle'); // 'idle', 'loading'
  const [isCollapsed, setIsCollapsed] = useState(false);
  const messagesEndRef = useRef(null);
  const inputRef = useRef(null);

  // Fetch all chats on initial load
  useEffect(() => {
    const fetchChats = async () => {
      try {
        const response = await fetch('/ai/conversations');
        if (!response.ok) throw new Error('Failed to fetch chats');

        const data = await response.json();
        setChats(data);
      } catch (error) {
        console.error('Error fetching chats:', error);
        // Fallback to empty array if fetch fails
        setChats([]);
      }
    };

    fetchChats();
  }, []);

  // Fetch messages when a chat is selected
  useEffect(() => {
    if (activeChatId) {
      const fetchMessages = async () => {
        try {
          const response = await fetch(`/ai/conversations/${activeChatId}`);
          if (!response.ok) throw new Error('Failed to fetch messages');

          const data = await response.json();
          setMessages(data);
        } catch (error) {
          console.error('Error fetching messages:', error);
          setMessages([]);
        }
      };

      fetchMessages();
    }
  }, [activeChatId]);

  // Auto-scroll to bottom of messages and focus input when messages change
  useEffect(() => {
    messagesEndRef.current?.scrollIntoView({ behavior: 'smooth' });

    // If we're not in loading state and we have messages, focus the input
    if (status === 'idle' && messages.length > 0) {
      inputRef.current?.focus();
    }
  }, [messages, status]);

  const handleChatSelect = (chatId) => {
    setActiveChatId(chatId);
    setView('chat');
  };

  const handleNewChat = async () => {
    try {
      const response = await fetch('/ai/conversations', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({ title: 'New Chat' }),
      });

      if (!response.ok) throw new Error('Failed to create new chat');

      const newChat = await response.json();
      setChats([...chats, newChat]);
      setActiveChatId(newChat.id);
      setMessages([]);
      setView('chat');
    } catch (error) {
      console.error('Error creating new chat:', error);
    }
  };

  const handleBackToSelection = () => {
    setView('selection');
    setActiveChatId(null);
  };

  const handleSendMessage = async () => {
    if (inputMessage.trim() === '' || status === 'loading') return;

    // Add user message to UI immediately
    const userMessage = { role: 'user', content: inputMessage };
    setMessages([...messages, userMessage]);
    setInputMessage('');
    setStatus('loading');

    try {
      const response = await fetch(`/ai/conversations/${activeChatId}`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({ message: inputMessage }),
      });

      if (!response.ok) throw new Error('Failed to send message');

      const data = await response.json();

      // Update messages with the response from API
      setMessages(prev => [...prev, ...data]);

      // Update chat list with the latest message
      setChats(prev =>
        prev.map(chat =>
          chat.id === activeChatId
            ? { ...chat, lastMessage: inputMessage }
            : chat
        )
      );

      // Focus back to the input textbox
      inputRef.current?.focus();
    } catch (error) {
      console.error('Error sending message:', error);
      // Add error message
      setMessages(prev => [...prev, {
        role: 'assistant',
        content: 'Sorry, there was an error processing your request.'
      }]);
    } finally {
      setStatus('idle');
    }
  };

  const handleKeyPress = (e) => {
    if (e.key === 'Enter' && !e.shiftKey) {
      e.preventDefault();
      handleSendMessage();
    }
  };

  // Chat Selection View
  const renderChatSelection = () => (
    <div className="flex flex-col h-full max-h-full overflow-hidden">
      <div className="flex-1 overflow-y-auto">
        {chats.length === 0 ? (
          <div className="p-4 text-center text-gray-500">
            No conversations yet. Start a new chat!
          </div>
        ) : (
          chats.map(chat => (
            <div
              key={chat.id}
              className="p-4 border-b border-gray-200 hover:bg-gray-100 cursor-pointer"
              onClick={() => handleChatSelect(chat.id)}
            >
              <div className="flex items-start">
                <div className="mr-3 mt-1">
                  <MessageSquare size={20} />
                </div>
                <div className="flex-1">
                  <div className="font-medium">{chat.summary || 'Untitled Chat'}</div>
                  <div className="text-sm text-gray-500 truncate">{chat.created_at ? 'Created: ' + (new Date(chat.created_at)).toISOString() : ''}</div>
                </div>
              </div>
            </div>
          ))
        )}
      </div>
      <div className="p-4 border-t border-gray-200 flex-shrink-0">
        <button
          className="w-full py-2 bg-blue-600 text-white rounded-md flex items-center justify-center"
          onClick={handleNewChat}
        >
          <Plus size={20} className="mr-2" />
          New Chat
        </button>
      </div>
    </div>
  );

  // Chat View
  const renderChatView = () => (
    <div className="flex flex-col h-full max-h-full overflow-hidden">
      <div className="flex-1 overflow-y-auto p-4 scrollbar-thin">
        {messages.length === 0 ? (
          <div className="text-center text-gray-500 mt-8">
            No messages yet. Send your first message below!
          </div>
        ) : (
          messages.map((message, index) => (
            <div
              key={index}
              className={`mb-4 ${message.role === 'user' ? 'flex justify-end' : 'flex justify-start'}`}
            >
              <div
                className={`max-w-3/4 p-3 rounded-lg ${message.role === 'user'
                  ? 'bg-blue-600 text-white rounded-br-none'
                  : 'bg-gray-200 text-gray-800 rounded-bl-none'
                  }`}
              >
                <MarkdownContent content={message.content} />
              </div>
            </div>
          ))
        )}
        {status === 'loading' && (
          <div className="flex justify-start mb-4">
            <div className="bg-gray-200 text-gray-800 p-3 rounded-lg rounded-bl-none">
              <div className="flex items-center">
                <Loader2 size={16} className="animate-spin mr-2" />
                <span>Typing...</span>
              </div>
            </div>
          </div>
        )}
        <div ref={messagesEndRef} />
      </div>

      <div className="p-4 border-t border-gray-200 flex-shrink-0">
        <div className="flex items-center rounded-md border border-gray-300 overflow-hidden">
          <textarea
            ref={inputRef}
            className="flex-1 p-3 focus:outline-none resize-none h-12 max-h-40"
            placeholder="Type your message..."
            value={inputMessage}
            onChange={(e) => setInputMessage(e.target.value)}
            onKeyDown={handleKeyPress}
            disabled={status === 'loading'}
          />
          <button
            className={`p-3 ${inputMessage.trim() && status !== 'loading' ? 'text-blue-600' : 'text-gray-400'}`}
            onClick={handleSendMessage}
            disabled={!inputMessage.trim() || status === 'loading'}
          >
            <Send size={20} />
          </button>
        </div>
      </div>
    </div>
  );

  return (
    <div className="fixed bottom-4 right-4 z-50">
      {isCollapsed ? (
        <button
          onClick={() => setIsCollapsed(false)}
          className="bg-blue-600 text-white p-4 rounded-full shadow-lg hover:bg-blue-700 transition-all duration-200 flex items-center justify-center"
        >
          <MessageSquare size={24} />
        </button>
      ) : (
        <div className="w-96 h-128 bg-white rounded-lg shadow-lg flex flex-col border border-gray-200 transition-all duration-200">
          <div className="flex items-center justify-between border-b border-gray-200 p-3">
            <h3 className="font-semibold">
              {view === 'selection' ? 'Live Chat' : (chats.find(chat => chat.id === activeChatId)?.summary || 'Chat')}
            </h3>
            <div className="flex">
              <button
                onClick={() => setIsCollapsed(true)}
                className="p-1 hover:bg-gray-100 rounded-full mr-1"
                title="Minimize"
              >
                <ChevronDown size={18} />
              </button>
              <button
                onClick={() => {
                  if (view === 'chat') {
                    handleBackToSelection();
                  } else {
                    setIsCollapsed(true);
                  }
                }}
                className="p-1 hover:bg-gray-100 rounded-full"
                title={view === 'chat' ? 'Back to Chats' : 'Close'}
              >
                {view === 'chat' ? <ArrowLeft size={18} /> : <X size={18} />}
              </button>
            </div>
          </div>
          <div className="flex-1 flex flex-col overflow-hidden">
            {view === 'selection' ? renderChatSelection() : renderChatView()}
          </div>
        </div>
      )}
    </div>
  );
};

export default ChatWidget;
