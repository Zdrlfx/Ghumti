import React from "react";
import { Bot, User } from "lucide-react";

export const ChatMessage = ({ message, isBot, timestamp }) => {
  return (
    <div className={`flex w-full mb-4 ${isBot ? "justify-start" : "justify-end"} animate-fade-in`}>
      <div className={`flex items-start max-w-[80%] ${isBot ? "flex-row" : "flex-row-reverse"}`}>
        <div
          className={`flex-shrink-0 w-8 h-8 rounded-full flex items-center justify-center 
          ${isBot ? "bg-gray-100 mr-2" : "bg-blue-100 ml-2"}`}
        >
          {isBot ? <Bot size={20} className="text-gray-600" /> : <User size={20} className="text-blue-600" />}
        </div>
        <div>
          <div
            className={`rounded-2xl px-4 py-2 ${
              isBot ? "bg-gray-100 text-gray-800" : "bg-blue-500 text-white"
            }`}
          >
            <p> className="text-sm"{message}</p>
          </div>
          <span className={`text-xs mt-1 ${isBot ? "text-left" : "text-right"} block text-gray-500`}>
            {timestamp}
          </span>
        </div>
      </div>
    </div>
  );
};
