import { useEffect, useRef, useState, useCallback } from 'react';

interface UseWebSocketOptions {
  onOpen?: () => void;
  onClose?: () => void;
  onError?: (error: Event) => void;
  reconnectAttempts?: number;
  reconnectInterval?: number;
}

export const useWebSocket = (url: string, options: UseWebSocketOptions = {}) => {
  const [lastMessage, setLastMessage] = useState<MessageEvent | null>(null);
  const [connected, setConnected] = useState(false);
  const wsRef = useRef<WebSocket | null>(null);
  const reconnectCountRef = useRef(0);

  const {
    onOpen,
    onClose,
    onError,
    reconnectAttempts = 5,
    reconnectInterval = 3000
  } = options;

  const connect = useCallback(() => {
    try {
      const ws = new WebSocket(url);
      wsRef.current = ws;

      ws.onopen = () => {
        setConnected(true);
        reconnectCountRef.current = 0;
        onOpen?.();
      };

      ws.onmessage = (event) => {
        setLastMessage(event);
      };

      ws.onclose = () => {
        setConnected(false);
        onClose?.();

        // Intentar reconectar
        if (reconnectCountRef.current < reconnectAttempts) {
          reconnectCountRef.current += 1;
          setTimeout(() => {
            connect();
          }, reconnectInterval);
        }
      };

      ws.onerror = (error) => {
        onError?.(error);
      };
    } catch (error) {
      console.error('WebSocket connection error:', error);
    }
  }, [url, onOpen, onClose, onError, reconnectAttempts, reconnectInterval]);

  const sendMessage = useCallback((message: any) => {
    if (wsRef.current?.readyState === WebSocket.OPEN) {
      const data = typeof message === 'string' ? message : JSON.stringify(message);
      wsRef.current.send(data);
      return true;
    }
    return false;
  }, []);

  const disconnect = useCallback(() => {
    if (wsRef.current) {
      wsRef.current.close();
      wsRef.current = null;
    }
    setConnected(false);
  }, []);

  useEffect(() => {
    connect();

    return () => {
      disconnect();
    };
  }, [connect, disconnect]);

  return {
    lastMessage,
    connected,
    sendMessage,
    disconnect,
    reconnect: connect
  };
};
