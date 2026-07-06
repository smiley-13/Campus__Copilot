import React, { useState, useRef, useEffect } from 'react';
import { chatWithAgent } from './services/api';
import './index.css';

// Specialized Data Renderer Component (Premium Design)
const DataRenderer = ({ data }) => {
  if (!data || !data.type) return null;

  switch (data.type) {
    case 'study_plan':
      return (
        <div className="premium-card study-card">
          <h4>Study Plan: {data.subject}</h4>
          <div className="meta-info">
            <span className="info-badge">⏱ {data.days_until_exam} days left</span>
            <span className="info-badge">⏳ {data.daily_hours} hrs/day</span>
          </div>
          <table className="data-table">
            <thead>
              <tr>
                <th>Topic</th>
                <th>Duration</th>
                <th>Strategy</th>
              </tr>
            </thead>
            <tbody>
              {data.sessions?.map((s, i) => (
                <tr key={i}>
                  <td className="font-medium">{s.topic}</td>
                  <td className="text-muted">{s.duration_minutes} min</td>
                  <td className="text-muted">{s.strategy}</td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>
      );
      
    case 'attendance':
      return (
        <div className="premium-card attendance-card">
          <h4>Attendance Status</h4>
          <div className="progress-container">
            <div 
              className="progress-ring" 
              style={{'--percentage': `${data.current_percentage}%`, '--ring-color': data.status === 'safe' ? '#10b981' : '#ef4444'}}
            >
              <div className="progress-inner">{data.current_percentage}%</div>
            </div>
            <div className="stats">
              <p className="text-muted">Attended: <strong className="text-main">{data.classes_attended} / {data.total_classes}</strong></p>
              {data.status === 'safe' ? (
                <p className="status safe">✓ Safe to miss {data.can_miss} classes</p>
              ) : (
                <p className="status danger">⚠ Need {data.classes_needed} classes for 75%</p>
              )}
            </div>
          </div>
        </div>
      );
      
    case 'assignment':
      return (
        <div className="premium-card assignment-card">
          <h4>{data.title}</h4>
          <div className="meta-info">
            <span className={`priority-badge ${data.urgency.toLowerCase()}`}>{data.urgency} Priority</span>
            <span className="info-badge">⏰ Due in {data.due_in_days} days</span>
          </div>
          <div className="stats-row">
            <div className="stat-box">
              <span className="stat-label">Priority Score</span>
              <span className="stat-value">{data.priority_score}</span>
            </div>
            <div className="stat-box highlight">
              <span className="stat-label">Recommended</span>
              <span className="stat-value">{data.daily_hours_needed} hrs/day</span>
            </div>
          </div>
        </div>
      );

    case 'career':
      return (
        <div className="premium-card career-card">
          <h4>Roadmap: {data.focus_area}</h4>
          <div className="tags">
            {data.skill_gaps?.map((gap, i) => <span key={i} className="tag error">{gap}</span>)}
          </div>
          <ul className="timeline">
            {data.roadmap?.map((step, i) => (
              <li key={i}>
                <strong className="text-main">{step.step}</strong>
                <p className="text-muted mt-1">{step.description}</p>
              </li>
            ))}
          </ul>
        </div>
      );
      
    default:
      return null;
  }
};

function App() {
  const [messages, setMessages] = useState([]);
  const [inputValue, setInputValue] = useState('');
  const [loading, setLoading] = useState(false);
  const [isDevMode, setIsDevMode] = useState(false);
  const messagesEndRef = useRef(null);

  const scrollToBottom = () => {
    messagesEndRef.current?.scrollIntoView({ behavior: 'smooth' });
  };

  useEffect(() => {
    scrollToBottom();
  }, [messages]);

  const handleSend = async (e, text = null) => {
    if (e) e.preventDefault();
    const userMessage = text || inputValue.trim();
    if (!userMessage) return;

    setMessages(prev => [...prev, { role: 'user', content: userMessage }]);
    setInputValue('');
    setLoading(true);

    try {
      const res = await chatWithAgent(userMessage);
      setMessages(prev => [...prev, { 
        role: 'agent', 
        content: res.content,
        agentName: res.agent_name,
        data: res.data,
        subResponses: res.sub_responses,
        used_tools: res.used_tools,
        detected_intents: res.detected_intents
      }]);
    } catch (error) {
      setMessages(prev => [...prev, { 
        role: 'agent', 
        content: 'I encountered an error connecting to the server. Please try again.',
        agentName: 'system_error'
      }]);
    } finally {
      setLoading(false);
    }
  };

  // Welcome Screen for empty state
  if (messages.length === 0) {
    return (
      <div className="app-layout">
        <Sidebar isDevMode={isDevMode} setIsDevMode={setIsDevMode} />
        <main className="welcome-container">
          <div className="welcome-content">
            <h1>Good morning</h1>
            <p className="welcome-subtitle">I'm your AI CampusCopilot. How can I assist you today?</p>
            
            <div className="suggestions-grid">
              <div className="suggestion-card" onClick={() => handleSend(null, "I have a DBMS exam in 5 days")}>
                <h4>Study Planner</h4>
                <p>Generate a revision schedule for an upcoming exam</p>
              </div>
              <div className="suggestion-card" onClick={() => handleSend(null, "I attended 32 out of 50 classes")}>
                <h4>Attendance</h4>
                <p>Calculate your shortage and get a recovery plan</p>
              </div>
              <div className="suggestion-card" onClick={() => handleSend(null, "I have an AI assignment due tomorrow")}>
                <h4>Assignments</h4>
                <p>Prioritize homework based on urgency and importance</p>
              </div>
              <div className="suggestion-card" onClick={() => handleSend(null, "Prepare me for Python interviews")}>
                <h4>Career & Placements</h4>
                <p>Identify skill gaps and create a preparation roadmap</p>
              </div>
            </div>

            <div className="chat-input-wrapper welcome-input">
              <form onSubmit={handleSend} className="input-form">
                <input
                  type="text"
                  value={inputValue}
                  onChange={(e) => setInputValue(e.target.value)}
                  placeholder="Message CampusCopilot..."
                  autoFocus
                />
                <button type="submit" disabled={!inputValue.trim()}>
                  <svg width="24" height="24" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round"><line x1="22" y1="2" x2="11" y2="13"></line><polygon points="22 2 15 22 11 13 2 9 22 2"></polygon></svg>
                </button>
              </form>
            </div>
          </div>
        </main>
      </div>
    );
  }

  return (
    <div className="app-layout">
      <Sidebar isDevMode={isDevMode} setIsDevMode={setIsDevMode} />

      <main className="chat-container">
        <div className="chat-messages">
          {messages.map((msg, index) => (
            <div key={index} className={`message-row ${msg.role}`}>
              {msg.role === 'agent' && (
                <div className="avatar agent-avatar">
                  <svg width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2"><path d="M12 2a2 2 0 0 1 2 2c0 .74-.4 1.39-1 1.73V7h1a7 7 0 0 1 7 7h1a2 2 0 0 1 0 4h-1v1a2 2 0 0 1-2 2H5a2 2 0 0 1-2-2v-1H2a2 2 0 0 1 0-4h1a7 7 0 0 1 7-7h1V5.73A2 2 0 0 1 12 2z"></path></svg>
                </div>
              )}
              {msg.role === 'user' && (
                <div className="avatar user-avatar">U</div>
              )}
              
              <div className="message-content">
                <p className="message-text">{msg.content}</p>
                
                {/* Data Renderer for Main Response */}
                <DataRenderer data={msg.data} />
                
                {/* Render data cards from Sub Responses but omit duplicate text */}
                {msg.subResponses && msg.subResponses.length > 0 && (
                  <div className="sub-responses-content">
                    {msg.subResponses.map((sub, i) => (
                      <DataRenderer key={i} data={sub.data} />
                    ))}
                  </div>
                )}

                {/* Developer Mode: Agent Execution Panel */}
                {isDevMode && msg.role === 'agent' && (
                  <div className="dev-panel">
                    <div className="dev-header">Agent Execution Trace</div>
                    <div className="dev-trace">
                      <div className="trace-step">
                        <span className="trace-icon">⚡</span>
                        <span className="trace-name">Planner</span>
                      </div>
                      
                      {/* Detected Intents */}
                      {msg.detected_intents && msg.detected_intents.length > 0 && (
                        <div className="trace-step nested">
                          <span className="trace-icon">↓</span>
                          <span className="trace-name" style={{color: '#aaa', fontStyle: 'italic'}}>
                            Detected Intent: {msg.detected_intents.join(', ')}
                          </span>
                        </div>
                      )}
                      
                      {msg.agentName !== 'planner_agent' && (
                        <div className="trace-step nested">
                          <span className="trace-icon">↓</span>
                          <span className="trace-name">{msg.agentName}</span>
                          {msg.used_tools?.map((tool, idx) => (
                            <div key={idx} className="tool-metrics">
                               <span className="trace-icon" style={{marginRight:'0.5rem', marginLeft: '-0.5rem'}}>↓</span>
                               <span className="tool-name">{tool.name}</span>
                               <span className="tool-time">{tool.execution_time_ms} ms</span>
                               <span className={`tool-status ${tool.success ? 'success' : 'error'}`}>{tool.success ? 'Success' : 'Failed'}</span>
                            </div>
                          ))}
                        </div>
                      )}

                      {msg.subResponses?.map((sub, i) => (
                        <div key={i} style={{display:'flex', flexDirection:'column', gap: '0.5rem'}}>
                          <div className="trace-step nested">
                            <span className="trace-icon">↓</span>
                            <span className="trace-name">{sub.agent_name}</span>
                          </div>
                          {sub.used_tools?.map((tool, idx) => (
                            <div key={idx} className="tool-metrics">
                               <span className="trace-icon" style={{marginRight:'0.5rem', marginLeft: '-0.5rem'}}>↓</span>
                               <span className="tool-name">{tool.name}</span>
                               <span className="tool-time">{tool.execution_time_ms} ms</span>
                               <span className={`tool-status ${tool.success ? 'success' : 'error'}`}>{tool.success ? 'Success' : 'Failed'}</span>
                            </div>
                          ))}
                        </div>
                      ))}
                    </div>
                  </div>
                )}
              </div>
            </div>
          ))}
          
          {loading && (
            <div className="message-row agent">
              <div className="avatar agent-avatar">
                <svg width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2"><path d="M12 2a2 2 0 0 1 2 2c0 .74-.4 1.39-1 1.73V7h1a7 7 0 0 1 7 7h1a2 2 0 0 1 0 4h-1v1a2 2 0 0 1-2 2H5a2 2 0 0 1-2-2v-1H2a2 2 0 0 1 0-4h1a7 7 0 0 1 7-7h1V5.73A2 2 0 0 1 12 2z"></path></svg>
              </div>
              <div className="message-content">
                <div className="typing-indicator">
                  <span></span><span></span><span></span>
                </div>
                {isDevMode && <div className="dev-status-text">Planner is routing intent...</div>}
              </div>
            </div>
          )}
          <div ref={messagesEndRef} />
        </div>

        <div className="chat-input-wrapper">
          <form onSubmit={handleSend} className="input-form">
            <input
              type="text"
              value={inputValue}
              onChange={(e) => setInputValue(e.target.value)}
              placeholder="Message CampusCopilot..."
              disabled={loading}
              autoFocus
            />
            <button type="submit" disabled={loading || !inputValue.trim()}>
              <svg width="24" height="24" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round"><line x1="22" y1="2" x2="11" y2="13"></line><polygon points="22 2 15 22 11 13 2 9 22 2"></polygon></svg>
            </button>
          </form>
          <div className="input-footer">AI can make mistakes. Consider verifying important academic dates.</div>
        </div>
      </main>
    </div>
  );
}

// Sidebar Component
const Sidebar = ({ isDevMode, setIsDevMode }) => (
  <aside className="sidebar">
    <div className="sidebar-header">
      <h2>CampusCopilot</h2>
    </div>
    <nav className="sidebar-nav">
      <button className="nav-item active">
        <svg width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2"><path d="M21 15a2 2 0 0 1-2 2H7l-4 4V5a2 2 0 0 1 2-2h14a2 2 0 0 1 2 2z"></path></svg>
        New Chat
      </button>
      
      <div className="nav-group">
        <button className="nav-item">📚 Study Planner</button>
        <button className="nav-item">✅ Attendance</button>
        <button className="nav-item">📝 Assignments</button>
        <button className="nav-item">💼 Career</button>
        <button className="nav-item disabled">🧠 Memory <span className="beta-tag">Soon</span></button>
      </div>

      <div className="sidebar-footer">
        {isDevMode && (
          <div className="agents-online-panel">
            <div className="nav-label">Agents Online (Dev)</div>
            <div className="agent-status"><span className="status-dot green"></span> Study Agent</div>
            <div className="agent-status"><span className="status-dot green"></span> Attendance Agent</div>
            <div className="agent-status"><span className="status-dot green"></span> Assignment Agent</div>
            <div className="agent-status"><span className="status-dot green"></span> Career Agent</div>
          </div>
        )}
        <label className="toggle-wrapper">
          <div className="toggle-text">Developer Mode</div>
          <div className={`toggle-switch ${isDevMode ? 'on' : 'off'}`} onClick={() => setIsDevMode(!isDevMode)}>
            <div className="toggle-knob"></div>
          </div>
        </label>
      </div>
    </nav>
  </aside>
);

export default App;
