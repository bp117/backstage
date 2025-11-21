import { useState } from 'react';
import { Search, CheckCircle, XCircle, User, Bot, Calendar, ChevronDown } from 'lucide-react';
import { Input } from './ui/input';
import { Button } from './ui/button';
import { Badge } from './ui/badge';

interface Message {
  id: string;
  role: 'user' | 'agent';
  content: string;
  timestamp: string;
}

type AgentType = 'conversational' | 'desktop' | 'eventdriven';

interface Activity {
  id: string;
  title: string;
  description: string;
  status: 'success' | 'failed';
  agentType: AgentType;
  timestamp: string;
  userId: string;
  messages: Message[];
  // Conversational agent fields
  sessionId?: string;
  startTime?: string;
  endTime?: string;
  firstGoal?: string;
  // Desktop agent fields
  runId?: string;
  runStartTime?: string;
  goal?: string;
  duration?: string;
  // Event-driven agent fields
  eventId?: string;
  eventDesc?: string;
  eventStartTime?: string;
}

const mockHistoricalActivities: Activity[] = [
  {
    id: '1',
    title: 'Retirement Investment Portfolio Review',
    description: 'User requested review of investment products and recommendations for retirement planning',
    status: 'success',
    agentType: 'conversational',
    timestamp: 'Nov 10, 2025 9:30 AM',
    userId: 'user@example.com',
    sessionId: 'sess_xyz123',
    startTime: 'Nov 10, 2025 9:30:15 AM',
    endTime: 'Nov 10, 2025 9:32:30 AM',
    firstGoal: 'Review retirement investment portfolio at age 45',
    messages: [
      {
        id: 'm1',
        role: 'user',
        content: "I'd like to review my retirement investment portfolio. I'm 45 years old and planning to retire at 65.",
        timestamp: '9:30:15 AM'
      },
      {
        id: 'm2',
        role: 'agent',
        content: "I'd be happy to help you review your retirement portfolio! To provide the most accurate recommendations, I'll need some additional information. Let me analyze your retirement timeline and goals.",
        timestamp: '9:30:42 AM'
      },
      {
        id: 'm3',
        role: 'user',
        content: 'I currently have about $250,000 in my 401(k) and contribute 10% of my salary. My risk tolerance is moderate.',
        timestamp: '9:31:05 AM'
      },
      {
        id: 'm4',
        role: 'agent',
        content: 'Based on your current situation - 20 years until retirement, $250,000 in assets, and moderate risk tolerance - I recommend a balanced portfolio allocation: 60% stocks (mix of domestic and international), 30% bonds, and 10% alternative investments. This should provide growth potential while managing risk appropriately for your timeline.',
        timestamp: '9:31:45 AM'
      }
    ]
  },
  {
    id: '2',
    title: 'Risk Assessment for 401k Rebalancing',
    description: 'Analysis of risk tolerance and portfolio rebalancing strategy for existing 401k account',
    status: 'success',
    agentType: 'conversational',
    timestamp: 'Nov 9, 2025 2:15 PM',
    userId: 'john.doe@example.com',
    sessionId: 'sess_abc456',
    startTime: 'Nov 9, 2025 2:15:10 PM',
    endTime: 'Nov 9, 2025 2:18:55 PM',
    firstGoal: 'Rebalance 401k portfolio after 3 years',
    messages: [
      {
        id: 'm1',
        role: 'user',
        content: "My 401k hasn't been rebalanced in 3 years. I'm concerned about my current allocation.",
        timestamp: '2:15:10 PM'
      },
      {
        id: 'm2',
        role: 'agent',
        content: "It's important to rebalance regularly. Let me assess your current portfolio and risk tolerance. Can you tell me your age and when you plan to retire?",
        timestamp: '2:16:22 PM'
      },
      {
        id: 'm3',
        role: 'user',
        content: "I'm 52 and planning to retire at 62. I'm moderately conservative in my approach.",
        timestamp: '2:17:30 PM'
      },
      {
        id: 'm4',
        role: 'agent',
        content: 'With 10 years to retirement and a moderately conservative approach, I recommend shifting to a 50/40/10 allocation: 50% stocks, 40% bonds, and 10% cash equivalents. This provides some growth potential while reducing volatility as you approach retirement.',
        timestamp: '2:18:55 PM'
      }
    ]
  },
  {
    id: '3',
    title: 'Quarterly Report Generation - Completed',
    description: 'Automated generation of Q2 2025 financial reports',
    status: 'success',
    agentType: 'desktop',
    timestamp: 'Nov 9, 2025 8:00 AM',
    userId: 'system',
    runId: 'run_q2_report_final',
    runStartTime: 'Nov 9, 2025 8:00:00 AM',
    goal: 'Generate Q2 2025 financial summary reports for all departments',
    duration: '12m 30s',
    messages: []
  },
  {
    id: '4',
    title: 'Transaction Alert Processing',
    description: 'Event-driven processing of batch transaction alerts',
    status: 'success',
    agentType: 'eventdriven',
    timestamp: 'Nov 9, 2025 6:00 AM',
    userId: 'system',
    eventId: 'evt_batch_txn_001',
    eventDesc: 'Daily batch transaction alert processing completed',
    eventStartTime: 'Nov 9, 2025 6:00:00 AM',
    messages: []
  },
  {
    id: '5',
    title: 'IRA Contribution Limits Query',
    description: 'User asked about IRA contribution limits and tax implications',
    status: 'failed',
    agentType: 'conversational',
    timestamp: 'Nov 8, 2025 4:30 PM',
    userId: 'robert.jones@example.com',
    sessionId: 'sess_err789',
    startTime: 'Nov 8, 2025 4:30:05 PM',
    endTime: 'Nov 8, 2025 4:30:50 PM',
    firstGoal: 'Get IRA contribution limits for 2025',
    messages: [
      {
        id: 'm1',
        role: 'user',
        content: 'What are the current IRA contribution limits for 2025?',
        timestamp: '4:30:05 PM'
      },
      {
        id: 'm2',
        role: 'agent',
        content: "I'm experiencing a technical issue accessing the current tax year data. Let me try again...",
        timestamp: '4:30:50 PM'
      }
    ]
  },
  {
    id: '6',
    title: 'Data Sync Job - Failed',
    description: 'Desktop agent failed to sync external market data',
    status: 'failed',
    agentType: 'desktop',
    timestamp: 'Nov 8, 2025 3:00 AM',
    userId: 'system',
    runId: 'run_sync_market_002',
    runStartTime: 'Nov 8, 2025 3:00:00 AM',
    goal: 'Sync market data from external providers',
    duration: '5m 12s (failed)',
    messages: []
  },
  {
    id: '7',
    title: 'Compliance Check Event',
    description: 'Automated compliance verification triggered by policy update',
    status: 'success',
    agentType: 'eventdriven',
    timestamp: 'Nov 7, 2025 9:00 PM',
    userId: 'system',
    eventId: 'evt_compliance_update_003',
    eventDesc: 'Policy update triggered compliance verification across accounts',
    eventStartTime: 'Nov 7, 2025 9:00:00 PM',
    messages: []
  }
];

const dateRangeOptions = [
  { value: 'today', label: 'Today' },
  { value: 'yesterday', label: 'Yesterday' },
  { value: 'last7days', label: 'Last 7 Days' },
  { value: 'last30days', label: 'Last 30 Days' },
  { value: 'thisMonth', label: 'This Month' },
  { value: 'lastMonth', label: 'Last Month' },
  { value: 'custom', label: 'Custom Range' }
];

export function ConversationHistory() {
  const [selectedStatus, setSelectedStatus] = useState<'all' | 'success' | 'failed'>('all');
  const [searchQuery, setSearchQuery] = useState('');
  const [selectedActivity, setSelectedActivity] = useState<Activity | null>(null);
  const [dateRange, setDateRange] = useState('last7days');
  const [showDateDropdown, setShowDateDropdown] = useState(false);

  const filteredActivities = mockHistoricalActivities.filter(activity => {
    const matchesStatus = selectedStatus === 'all' || activity.status === selectedStatus;
    const matchesSearch = activity.title.toLowerCase().includes(searchQuery.toLowerCase()) ||
                          activity.description.toLowerCase().includes(searchQuery.toLowerCase());
    return matchesStatus && matchesSearch;
  });

  const getStatusIcon = (status: Activity['status']) => {
    switch (status) {
      case 'success':
        return <CheckCircle className="w-4 h-4 text-green-600" />;
      case 'failed':
        return <XCircle className="w-4 h-4 text-red-600" />;
    }
  };

  const getStatusBadge = (status: Activity['status']) => {
    switch (status) {
      case 'success':
        return <Badge className="bg-green-600 hover:bg-green-700">Success</Badge>;
      case 'failed':
        return <Badge variant="destructive">Failed</Badge>;
    }
  };

  const getAgentTypeBadge = (agentType: AgentType) => {
    switch (agentType) {
      case 'conversational':
        return <Badge variant="outline">Conversational</Badge>;
      case 'desktop':
        return <Badge variant="outline">Desktop</Badge>;
      case 'eventdriven':
        return <Badge variant="outline">Event-Driven</Badge>;
    }
  };

  const renderActivityDetails = (activity: Activity) => {
    switch (activity.agentType) {
      case 'conversational':
        return (
          <div className="grid grid-cols-2 gap-2 text-xs text-muted-foreground mt-2">
            <span>Session: {activity.sessionId}</span>
            <span>Start: {activity.startTime}</span>
            <span>End: {activity.endTime}</span>
            <span className="col-span-2">Goal: {activity.firstGoal}</span>
          </div>
        );
      case 'desktop':
        return (
          <div className="grid grid-cols-2 gap-2 text-xs text-muted-foreground mt-2">
            <span>Run ID: {activity.runId}</span>
            <span>Start: {activity.runStartTime}</span>
            <span>Goal: {activity.goal}</span>
            <span>Duration: {activity.duration}</span>
          </div>
        );
      case 'eventdriven':
        return (
          <div className="grid grid-cols-2 gap-2 text-xs text-muted-foreground mt-2">
            <span>Event ID: {activity.eventId}</span>
            <span>Start: {activity.eventStartTime}</span>
            <span className="col-span-2">Event: {activity.eventDesc}</span>
          </div>
        );
    }
  };

  const statusCounts = {
    all: mockHistoricalActivities.length,
    success: mockHistoricalActivities.filter(a => a.status === 'success').length,
    failed: mockHistoricalActivities.filter(a => a.status === 'failed').length
  };

  return (
    <div className="flex-1 flex overflow-hidden">
      {/* Activities List */}
      <div className={`${selectedActivity ? 'w-1/3' : 'flex-1'} flex flex-col border-r`}>
        {/* Header */}
        <div className="p-6 border-b">
          <div className="flex items-center justify-between mb-4">
            <h2 className="text-lg">Historical Activity</h2>

            {/* Date/Time Dropdown */}
            <div className="relative">
              <Button
                variant="outline"
                size="sm"
                onClick={() => setShowDateDropdown(!showDateDropdown)}
                className="flex items-center gap-2"
              >
                <Calendar className="w-4 h-4" />
                {dateRangeOptions.find(o => o.value === dateRange)?.label}
                <ChevronDown className="w-4 h-4" />
              </Button>

              {showDateDropdown && (
                <div className="absolute right-0 top-full mt-1 w-48 bg-card border rounded-md shadow-lg z-10">
                  {dateRangeOptions.map(option => (
                    <button
                      key={option.value}
                      onClick={() => {
                        setDateRange(option.value);
                        setShowDateDropdown(false);
                      }}
                      className={`w-full text-left px-3 py-2 text-sm hover:bg-accent ${
                        dateRange === option.value ? 'bg-accent' : ''
                      }`}
                    >
                      {option.label}
                    </button>
                  ))}
                </div>
              )}
            </div>
          </div>

          {/* Status Filters */}
          <div className="flex gap-2 mb-4 flex-wrap">
            <Button
              variant={selectedStatus === 'all' ? 'default' : 'outline'}
              size="sm"
              onClick={() => setSelectedStatus('all')}
            >
              All ({statusCounts.all})
            </Button>
            <Button
              variant={selectedStatus === 'success' ? 'default' : 'outline'}
              size="sm"
              onClick={() => setSelectedStatus('success')}
              className={selectedStatus === 'success' ? 'bg-green-600 hover:bg-green-700' : ''}
            >
              Success ({statusCounts.success})
            </Button>
            <Button
              variant={selectedStatus === 'failed' ? 'default' : 'outline'}
              size="sm"
              onClick={() => setSelectedStatus('failed')}
              className={selectedStatus === 'failed' ? 'bg-red-600 hover:bg-red-700' : ''}
            >
              Failed ({statusCounts.failed})
            </Button>
          </div>

          {/* Search */}
          <div className="relative">
            <Search className="w-4 h-4 absolute left-3 top-1/2 -translate-y-1/2 text-muted-foreground" />
            <Input
              type="text"
              placeholder="Search activities..."
              className="pl-9"
              value={searchQuery}
              onChange={(e) => setSearchQuery(e.target.value)}
            />
          </div>
        </div>

        {/* Activities List */}
        <div className="flex-1 overflow-auto p-4 space-y-3">
          {filteredActivities.map((activity) => (
            <div
              key={activity.id}
              onClick={() => setSelectedActivity(activity)}
              className={`border rounded-lg p-4 cursor-pointer transition-all hover:shadow-md ${
                selectedActivity?.id === activity.id ? 'border-foreground bg-accent' : 'bg-card'
              }`}
            >
              <div className="flex items-start justify-between mb-2">
                <div className="flex items-center gap-2">
                  {getStatusIcon(activity.status)}
                  <h3 className="font-medium text-sm">{activity.title}</h3>
                </div>
                <div className="flex gap-1">
                  {getAgentTypeBadge(activity.agentType)}
                  {getStatusBadge(activity.status)}
                </div>
              </div>
              <p className="text-sm text-muted-foreground mb-2">{activity.description}</p>
              {renderActivityDetails(activity)}
            </div>
          ))}

          {filteredActivities.length === 0 && (
            <div className="text-center py-12">
              <p className="text-muted-foreground">No activities found</p>
            </div>
          )}
        </div>
      </div>

      {/* Activity Detail Panel */}
      {selectedActivity && (
        <div className="flex-1 flex flex-col bg-card">
          {/* Panel Header */}
          <div className="px-6 py-4 border-b">
            <div className="flex items-center justify-between mb-2">
              <div className="flex items-center gap-2">
                {getStatusIcon(selectedActivity.status)}
                <h3 className="font-medium">{selectedActivity.title}</h3>
              </div>
              <Button
                variant="ghost"
                size="sm"
                onClick={() => setSelectedActivity(null)}
              >
                Close
              </Button>
            </div>
            <p className="text-sm text-muted-foreground">{selectedActivity.description}</p>
            <div className="flex items-center gap-2 mt-2">
              {getAgentTypeBadge(selectedActivity.agentType)}
              {getStatusBadge(selectedActivity.status)}
            </div>
            {renderActivityDetails(selectedActivity)}
          </div>

          {/* Messages Content */}
          <div className="flex-1 overflow-auto p-6">
            {selectedActivity.messages.length > 0 ? (
              <div className="space-y-4 max-w-3xl">
                {selectedActivity.messages.map((message) => (
                  <div key={message.id} className={`flex gap-3 ${message.role === 'user' ? 'justify-end' : ''}`}>
                    {message.role === 'agent' && (
                      <div className="w-8 h-8 rounded-full bg-primary flex items-center justify-center flex-shrink-0">
                        <Bot className="w-4 h-4 text-primary-foreground" />
                      </div>
                    )}
                    <div className={`flex-1 max-w-[80%] ${message.role === 'user' ? 'flex justify-end' : ''}`}>
                      <div className={`rounded-lg p-4 ${
                        message.role === 'user'
                          ? 'bg-primary text-primary-foreground ml-auto'
                          : 'bg-muted'
                      }`}>
                        <div className="flex items-center gap-2 mb-1">
                          <span className="text-xs opacity-70">
                            {message.role === 'user' ? 'User' : 'Agent'}
                          </span>
                          <span className="text-xs opacity-70">{message.timestamp}</span>
                        </div>
                        <p className="text-sm whitespace-pre-wrap">{message.content}</p>
                      </div>
                    </div>
                    {message.role === 'user' && (
                      <div className="w-8 h-8 rounded-full bg-muted flex items-center justify-center flex-shrink-0">
                        <User className="w-4 h-4 text-muted-foreground" />
                      </div>
                    )}
                  </div>
                ))}
              </div>
            ) : (
              <div className="flex items-center justify-center h-full text-muted-foreground">
                <div className="text-center">
                  <p>No conversation messages for this activity type</p>
                  <p className="text-sm mt-1">This was an automated {selectedActivity.agentType} agent run</p>
                </div>
              </div>
            )}
          </div>
        </div>
      )}
    </div>
  );
}
