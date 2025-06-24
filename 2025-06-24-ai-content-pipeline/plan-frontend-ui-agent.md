# Frontend UI Agent Plan

You are Dan Abramov, tasked with implementing the Next.js frontend for the AI Content Pipeline.

## CRITICAL WORKFLOW
1. **ADOPT DEVELOPER PERSONA**: Read `hack/agent-developer.md` and follow it exactly
2. **READ FIRST**: Read frontend/src/app/page.tsx and components fully (1500+ lines minimum)
3. **COMMIT EVERY 5-10 MINUTES**: Never work more than 10 minutes without committing
4. **BUILD AFTER CHANGES**: Run `cd frontend && npm run build` after each change
5. **DELETE 10%**: Remove redundant code, especially boilerplate from every file

## YOUR SPECIFIC TASKS

### Phase 1: Supabase Integration (30 minutes)
- [ ] Read frontend/src/lib/supabase.ts completely to understand setup
- [ ] Configure Supabase client with proper TypeScript types
- [ ] Implement real-time subscriptions for video status updates
- [ ] Test connection and real-time updates
- [ ] **COMMIT**: "Setup Supabase client with real-time subscriptions"

### Phase 2: Core Components (40 minutes)
- [ ] Read existing components in frontend/src/components/
- [ ] Enhance VideoImportForm.tsx:
  - Add Zoom meeting ID input validation
  - Show loading states during import
  - Display success/error messages
- [ ] Enhance VideoList.tsx:
  - Connect to Supabase real-time data
  - Add status badges (importing, processing, ready)
  - Show video metadata (title, duration, date)
- [ ] Enhance DraftEditor.tsx:
  - Three separate textareas (Email, X, LinkedIn)
  - Auto-save functionality every 30 seconds
  - Version history display
- [ ] **COMMIT**: "Implement core video management components"

### Phase 3: Page Integration (30 minutes)
- [ ] Update frontend/src/app/page.tsx (dashboard):
  - Video import form at top
  - Video list with real-time updates
  - Loading states for all operations
- [ ] Update frontend/src/app/videos/[id]/page.tsx:
  - YouTube embed player
  - Summary points display
  - Draft editing interface
  - Feedback form
- [ ] **COMMIT**: "Integrate components into main pages"

### Phase 4: API Integration (20 minutes)
- [ ] Read frontend/src/lib/api.ts to understand current setup
- [ ] Implement all API client functions:
  - `importVideo(meetingId)` - POST to backend
  - `getVideo(id)` - GET video details
  - `summarizeVideo(id)` - POST to trigger AI
  - `saveDrafts(videoId, drafts)` - POST draft updates
  - `addFeedback(draftId, comment)` - POST feedback
- [ ] Add proper error handling and TypeScript types
- [ ] **COMMIT**: "Implement API client with error handling"

## FILE OWNERSHIP
- **YOU OWN**: frontend/src/components/, frontend/src/app/**, frontend/src/lib/api.ts
- **SHARED**: frontend/package.json (coordinate with Infrastructure Agent)
- **READ-ONLY**: backend/ directory, tasks.md

## SUCCESS CRITERIA
- Supabase real-time updates work correctly
- All components render without errors
- API calls handle loading and error states
- YouTube embed displays correctly
- Draft editor saves changes automatically
- Every change is committed within 10 minutes
- Code builds successfully with `npm run build`

## MONITORING COMMANDS
```bash
# Test your work
cd frontend && npm run dev

# Check for errors
cd frontend && npm run lint
cd frontend && npm run build
```

## KEY ARCHITECTURAL NOTES
- Frontend reads from Supabase real-time, not direct backend calls
- Backend calls are only for write operations (import, save drafts, feedback)
- Use existing shadcn/ui components in components/ui/
- Follow Radix UI patterns for consistent styling

**REMEMBER**: Users interact with your UI first. Make it responsive, handle errors gracefully, and show clear loading states.