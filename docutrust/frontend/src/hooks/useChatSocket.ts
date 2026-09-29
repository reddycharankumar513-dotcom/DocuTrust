import { useCallback, useEffect, useRef, useState } from "react";
import { chatSocketUrl } from "@/services/api";
import type { AgentLog, ChatResponse } from "@/types";

type SocketEvent =
  | { type: "agent_log"; payload: AgentLog }
  | { type: "answer_chunk"; payload: { content: string } }
  | { type: "final_answer"; payload: ChatResponse };

export function useChatSocket(
  token: string | null,
  onLog: (log: AgentLog) => void,
  onChunk: (chunk: string) => void,
  onAnswer: (answer: ChatResponse) => void
) {
  const [connected, setConnected] = useState(false);
  const socketRef = useRef<WebSocket | null>(null);
  const callbacksRef = useRef({ onLog, onChunk, onAnswer });

  useEffect(() => {
    callbacksRef.current = { onLog, onChunk, onAnswer };
  }, [onLog, onChunk, onAnswer]);

  useEffect(() => {
    if (!token) {
      return;
    }

    const socket = new WebSocket(chatSocketUrl(token));
    socketRef.current = socket;
    socket.onopen = () => setConnected(true);
    socket.onclose = () => setConnected(false);
    socket.onerror = () => setConnected(false);
    socket.onmessage = (event) => {
      const message = JSON.parse(event.data) as SocketEvent;
      if (message.type === "agent_log") {
        callbacksRef.current.onLog(message.payload);
      }
      if (message.type === "answer_chunk") {
        callbacksRef.current.onChunk(message.payload.content);
      }
      if (message.type === "final_answer") {
        callbacksRef.current.onAnswer(message.payload);
      }
    };

    return () => {
      socket.close();
      socketRef.current = null;
      setConnected(false);
    };
  }, [token]);

  const sendQuestion = useCallback((question: string, topK: number) => {
    const socket = socketRef.current;
    if (!socket || socket.readyState !== WebSocket.OPEN) {
      return false;
    }
    socket.send(JSON.stringify({ question, top_k: topK }));
    return true;
  }, []);

  return { connected, sendQuestion };
}
