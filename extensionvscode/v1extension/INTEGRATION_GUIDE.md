# AI Goals Tracker - Integration Guide

## 🔗 Connecting Extension to Backend V2

This guide explains how to connect the VSCode extension to the AI Goals Tracker V2 backend.

## Prerequisites

1. **Backend running** - The AI Goals Tracker V2 backend must be running
2. **Node.js 16+** - For the VSCode extension
3. **VSCode 1.75+** - To run the extension

## Quick Start

### Step 1: Start the Backend

```bash
cd v2extension
docker-compose up -d

# Verify backend is running
curl http://localhost:8000/health
# Should return: {"status":"healthy"}
```

### Step 2: Install Extension Dependencies

```bash
cd v1extension
npm install
```

### Step 3: Configure Extension

Open VSCode Settings (`Cmd+,` or `Ctrl+,`) and search for "AI Goals Tracker":

```json
{
  "aiGoalsTracker.backendApiUrl": "http://localhost:8000",
  "aiGoalsTracker.backendWsUrl": "ws://localhost:8000/api/v1/ws",
  "aiGoalsTracker.userId": "your-user-id", // Auto-generated if empty
  "aiGoalsTracker.enableBackend": true,
  "aiGoalsTracker.enableWebSocket": true,
  "aiGoalsTracker.syncInterval": 30 // seconds
}
```

Or create `.vscode/settings.json` in your workspace:

```json
{
  "aiGoalsTracker.backendApiUrl": "http://localhost:8000",
  "aiGoalsTracker.enableBackend": true,
  "aiGoalsTracker.enableWebSocket": true
}
```

### Step 4: Run the Extension

#### Option A: Development Mode (F5)

1. Open `v1extension` folder in VSCode
2. Press `F5` to start debugging
3. A new VSCode window will open with the extension loaded
4. Open the "AI Goals Tracker" view in the Activity Bar

#### Option B: Compile and Install

```bash
# Compile TypeScript
npm run compile

# Package extension
vsce package

# Install .vsix file
code --install-extension ai-goals-tracker-0.0.1.vsix
```

### Step 5: Verify Connection

1. Open the "AI Goals Tracker" view
2. You should see:
   - ✅ Message: "Connected to backend at http://localhost:8000"
   - Goals loaded from backend (if any exist)

3. Check the Output panel:
   - View → Output
   - Select "AI Goals Tracker - Backend" from dropdown
   - You should see connection logs

## Features

### ✅ Implemented

1. **REST API Integration**
   - Create goals
   - List goals
   - Update goals
   - Delete goals
   - Create tasks
   - Complete tasks
   - Rate limit status

2. **WebSocket Real-time Updates**
   - Goal created notifications
   - Goal updated notifications
   - Task completed notifications
   - Code validation results

3. **Auto-sync**
   - Configurable sync interval
   - Background synchronization

4. **Rate Limiting**
   - View current rate limit status
   - Backend tracks all requests

### Commands

All commands are available in the Command Palette (`Cmd+Shift+P` or `Ctrl+Shift+P`):

| Command | Description |
|---------|-------------|
| `AI Goals Tracker: Refresh Goals` | Sync with backend |
| `AI Goals Tracker: Add New Goal` | Create a new goal |
| `AI Goals Tracker: Delete Goal` | Delete selected goal |
| `AI Goals Tracker: Start Goal` | Mark goal as in progress |
| `AI Goals Tracker: Validate Task` | Mark task as completed |
| `AI Goals Tracker: Show Backend Output` | View backend logs |
| `AI Goals Tracker: Show Rate Limits` | View rate limit status |
| `AI Goals Tracker: Clear All Goals` | Delete all goals |

### TreeView Actions

Right-click on goals/tasks in the tree view:

- **Goal Actions**:
  - ▶️ Start Goal
  - 🗑️ Delete Goal
  - ✏️ (Click to view details)

- **Task Actions**:
  - ✅ Validate Task (mark as completed)

## Architecture

```
┌─────────────────────────────────────────┐
│   VSCode Extension (TypeScript)         │
│                                         │
│  ┌──────────────┐  ┌──────────────┐   │
│  │   TreeView   │  │  WebView     │   │
│  │   Provider   │  │  Panels      │   │
│  └──────────────┘  └──────────────┘   │
│         │                  │            │
│  ┌──────▼──────────────────▼────────┐  │
│  │    BackendService               │  │
│  │  - REST API (axios)             │  │
│  │  - WebSocket (ws)               │  │
│  └──────┬──────────────────┬───────┘  │
└─────────┼──────────────────┼──────────┘
          │                  │
          │ HTTP             │ WebSocket
          ▼                  ▼
┌─────────────────────────────────────────┐
│   FastAPI Backend                       │
│                                         │
│  ┌──────────┐  ┌──────────┐           │
│  │   API    │  │WebSocket │           │
│  │ Endpoints│  │  Server  │           │
│  └──────────┘  └──────────┘           │
└─────────────────────────────────────────┘
```

## Code Structure

### New Files Created

1. **`src/backendService.ts`** - Main backend integration service
   - REST API client
   - WebSocket connection
   - Event handling
   - Auto-reconnection

2. **`src/config.ts`** - Configuration management
   - Read VSCode settings
   - Generate user ID
   - Environment configuration

3. **`src/extensionV2.ts`** - Extension entry point (V2)
   - Backend integration
   - Command registration
   - WebSocket event handlers
   - Auto-sync

### Modified Files

1. **`package.json`**
   - Added backend configuration settings
   - Added `ws` dependency

### Backend Service API

```typescript
// Create backend service
const backend = new BackendService({
    apiUrl: 'http://localhost:8000',
    wsUrl: 'ws://localhost:8000/api/v1/ws',
    userId: 'your-user-id'
});

// REST API
await backend.healthCheck();
const goals = await backend.getGoals();
const goal = await backend.createGoal({ title, description, user_id });
await backend.updateGoal(goalId, { status: 'in_progress' });
await backend.deleteGoal(goalId);

const tasks = await backend.getTasks(goalId);
const task = await backend.createTask({ title, description, goal_id, user_id });
await backend.completeTask(taskId);

// WebSocket
backend.connectWebSocket();
backend.on('goal_created', (data) => {
    console.log('Goal created:', data);
});
backend.on('task_completed', (data) => {
    console.log('Task completed:', data);
});

// Cleanup
backend.dispose();
```

## Troubleshooting

### Backend Not Reachable

**Error:** "Backend is not reachable at http://localhost:8000"

**Solution:**
```bash
# Check if backend is running
curl http://localhost:8000/health

# If not running, start it
cd v2extension
docker-compose up -d

# Check logs
docker-compose logs backend
```

### WebSocket Not Connecting

**Error:** WebSocket connection failed

**Solutions:**
1. Check if WebSocket is enabled:
   ```json
   { "aiGoalsTracker.enableWebSocket": true }
   ```

2. Verify WebSocket URL:
   ```json
   { "aiGoalsTracker.backendWsUrl": "ws://localhost:8000/api/v1/ws" }
   ```

3. Check backend logs:
   ```bash
   docker-compose logs -f backend
   ```

### Goals Not Syncing

**Error:** Goals not appearing in tree view

**Solutions:**
1. Click "Refresh" button in tree view
2. Check backend connection in Output panel
3. Verify user ID matches backend data
4. Check rate limits: `Show Rate Limits` command

### Rate Limit Exceeded

**Error:** HTTP 429 - Rate limit exceeded

**Solution:**
Wait for the retry-after period or reset limits:
```bash
curl -X POST http://localhost:8000/api/v1/admin/rate-limits/users/your-user-id/reset
```

### Extension Not Loading

**Error:** Extension fails to activate

**Solutions:**
1. Check console output: Help → Toggle Developer Tools
2. Verify all dependencies installed: `npm install`
3. Recompile: `npm run compile`
4. Check `extension.ts` or `extensionV2.ts` is correct

## Development Workflow

### Using Extension with Backend

1. **Start backend first:**
   ```bash
   cd v2extension
   docker-compose up -d
   ```

2. **Start extension in debug mode:**
   - Open `v1extension` in VSCode
   - Press `F5`
   - Extension window opens

3. **Test integration:**
   - Create a goal in extension → Check backend
   - Create a goal via API → Check extension auto-sync

### Testing API Directly

```bash
# Create goal via API
curl -X POST http://localhost:8000/api/v1/goals \
  -H "Content-Type: application/json" \
  -d '{
    "title": "Test Goal",
    "description": "Testing integration",
    "user_id": "your-user-id"
  }'

# Goal should appear in extension after sync interval
# Or click Refresh button
```

### Debugging WebSocket

1. Open Output panel: View → Output
2. Select "AI Goals Tracker - Backend"
3. Watch for WebSocket connection logs
4. Trigger events from backend and watch extension react

## Migration from V1 to V2

If you were using the old local storage version:

1. **Export goals from V1** (if needed):
   - Goals are stored in `.vscode/.ai-goals-tracker.json`
   - You can manually create them in backend via API

2. **Switch to V2**:
   - Update `extension.ts` to use `extensionV2.ts`
   - Or rename `extensionV2.ts` to `extension.ts`

3. **Configure backend**:
   - Add backend settings (see Step 3 above)

4. **Test connection**:
   - Restart extension
   - Verify connection message

## Advanced Configuration

### Custom Backend URL

```json
{
  "aiGoalsTracker.backendApiUrl": "https://your-backend.com",
  "aiGoalsTracker.backendWsUrl": "wss://your-backend.com/api/v1/ws"
}
```

### Multiple Users

Each user needs a unique ID:

```json
{
  "aiGoalsTracker.userId": "user-123"
}
```

### Course-specific Goals

```json
{
  "aiGoalsTracker.courseId": "course-456"
}
```

Goals will be filtered by course.

### Disable Features

```json
{
  "aiGoalsTracker.enableWebSocket": false, // Disable real-time updates
  "aiGoalsTracker.syncInterval": 0 // Disable auto-sync
}
```

## Production Deployment

### Backend Production URL

```json
{
  "aiGoalsTracker.backendApiUrl": "https://api.your-domain.com",
  "aiGoalsTracker.backendWsUrl": "wss://api.your-domain.com/api/v1/ws"
}
```

### Publishing Extension

```bash
# Install vsce
npm install -g @vscode/vsce

# Package
vsce package

# Publish to marketplace
vsce publish
```

## Support

- **Backend Docs:** See `v2extension/README.md`
- **Rate Limiting:** See `v2extension/backend/RATE_LIMITING.md`
- **Docker Setup:** See `v2extension/DOCKER_SETUP.md`

---

**Integration Version:** 1.0.0
**Last Updated:** December 28, 2024
