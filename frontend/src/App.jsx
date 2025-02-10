import React, { useState, useRef, useEffect } from "react";
import { Send, Moon, Sun, Bus, ArrowRight } from "lucide-react";
import { ChatMessage } from "./components/ChatMessage";
import { TypingIndicator } from "./components/TypingIndicator";
import Map from "./components/Map"; // Import the Map component

function App() {
  const [messages, setMessages] = useState([
    {
      text: "Hello! How can I help you today?",
      isBot: true,
      timestamp: new Date().toLocaleTimeString(),
    },
  ]);
  const [inputMessage, setInputMessage] = useState("");
  const [isLoading, setIsLoading] = useState(false);
  const [darkMode, setDarkMode] = useState(false);
  const [showChat, setShowChat] = useState(false);
  const [showMap, setShowMap] = useState(false); // Controls map visibility
  const messagesEndRef = useRef(null);

  const scrollToBottom = () => {
    if (messagesEndRef.current) {
      messagesEndRef.current.scrollIntoView({ behavior: "smooth" });
    }
  };

  useEffect(() => {
    scrollToBottom();
  }, [messages]);

  const handleSendMessage = async () => {
    if (!inputMessage.trim()) return;

    const newMessage = {
      text: inputMessage,
      isBot: false,
      timestamp: new Date().toLocaleTimeString(),
    };

    setMessages((prev) => [...prev, newMessage]);
    setInputMessage("");
    setIsLoading(true);

    try {
      const response = await fetch("http://127.0.0.1:8000/chat", {
        method: "POST",
        headers: {
          "Content-Type": "application/json",
        },
        body: JSON.stringify({ message: inputMessage }),
      });

      if (!response.ok) {
        throw new Error("Server error. Please try again.");
      }

      const data = await response.json();

      setMessages((prev) => [
        ...prev,
        {
          text: data.message || "I apologize, but I'm unable to process your request at the moment.",
          isBot: true,
          timestamp: new Date().toLocaleTimeString(),
        },
      ]);

      // Show the map after receiving a response
      setShowMap(true);
    } catch (error) {
      setMessages((prev) => [
        ...prev,
        {
          text: "I apologize, but I'm having trouble connecting to the server.",
          isBot: true,
          timestamp: new Date().toLocaleTimeString(),
        },
      ]);
    } finally {
      setIsLoading(false);
    }
  };

  const handleKeyPress = (e) => {
    if (e.key === "Enter" && !e.shiftKey) {
      e.preventDefault();
      handleSendMessage();
    }
  };

  const startChat = () => {
    setShowChat(true);
  };

  if (!showChat) {
    return (
      <div className={`min-h-screen ${darkMode ? "bg-gray-900" : "bg-gradient-to-br from-blue-50 to-purple-50"}`}>
        <div className="container mx-auto px-4 py-8 max-w-4xl h-screen flex flex-col items-center justify-center">
          <div className={`w-full max-w-md text-center ${darkMode ? "text-white" : "text-gray-800"}`}>
            <div className="mb-8">
              <div className="inline-block p-4 rounded-full bg-blue-500 mb-6">
                <Bus size={48} className="text-white" />
              </div>
              <h1 className="text-4xl font-bold mb-4">Ghumti</h1>
              <p className="text-xl mb-8">Your Local Bus Assistant</p>
              <p className="text-base mb-12 text-gray-600 dark:text-gray-300">
                Get accurate local bus route info, nearest stops, and travel guidance!
              </p>
              <button
                onClick={startChat}
                className="inline-flex items-center px-6 py-3 bg-blue-500 text-white rounded-full hover:bg-blue-600 transition-colors font-medium text-lg"
              >
                Start Chatting
                <ArrowRight className="ml-2 w-5 h-5" />
              </button>
            </div>
            <button
              onClick={() => setDarkMode(!darkMode)}
              className={`p-2 rounded-full ${darkMode ? "hover:bg-gray-700 bg-gray-800" : "hover:bg-gray-100 bg-white"} shadow-md`}
            >
              {darkMode ? <Sun className="w-5 h-5 text-white" /> : <Moon className="w-5 h-5 text-gray-600" />}
            </button>
          </div>
        </div>
      </div>
    );
  }

  return (
    <div className={`min-h-screen ${darkMode ? "bg-gray-900" : "bg-gradient-to-br from-blue-50 to-purple-50"}`}>
      <div className="container mx-auto px-4 py-8 flex space-x-4">
        {/* Chat Section */}
        <div className="w-2/3 rounded-xl shadow-lg overflow-hidden">
          <div className="p-4 border-b flex justify-between items-center">
            <div className="flex items-center">
              <Bus className="w-6 h-6 mr-2 text-gray-800" />
              <h1 className="text-xl font-semibold text-gray-800">Ghumti Assistant</h1>
            </div>
            <button onClick={() => setDarkMode(!darkMode)} className="p-2 rounded-full hover:bg-gray-100">
              {darkMode ? <Sun className="w-5 h-5 text-white" /> : <Moon className="w-5 h-5 text-gray-600" />}
            </button>
          </div>

          {/* Chat Messages */}
          <div className="h-[600px] overflow-y-auto p-4 bg-white">
            {messages.map((message, index) => (
              <ChatMessage key={index} message={message.text} isBot={message.isBot} timestamp={message.timestamp} />
            ))}
            {isLoading && <TypingIndicator />}
            <div ref={messagesEndRef} />
          </div>

          {/* Input Area */}
          <div className="p-4 border-t bg-white">
            <div className="flex space-x-2">
              <input
                type="text"
                value={inputMessage}
                onChange={(e) => setInputMessage(e.target.value)}
                onKeyPress={handleKeyPress}
                placeholder="Type a message..."
                className="flex-1 px-4 py-2 rounded-full border bg-gray-50 focus:ring-blue-400"
              />
              <button onClick={handleSendMessage} disabled={!inputMessage.trim() || isLoading} className="p-2 rounded-full bg-blue-500 hover:bg-blue-600">
                <Send className="w-5 h-5 text-white" />
              </button>
            </div>
          </div>
        </div>

        {/* Map Section */}
        {showMap && <div className="w-1/3 rounded-xl shadow-lg overflow-hidden"><Map /></div>}
      </div>
    </div>
  );
}

export default App;
