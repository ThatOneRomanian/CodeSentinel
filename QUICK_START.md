# 🚀 CodeSentinel Phase 3 GUI - Quick Reference

## Installation (2 minutes)

```bash
# Option A: Automatic (Recommended)
./setup-gui.sh

# Option B: Manual
pip install fastapi uvicorn python-multipart
cd gui && npm install
```

## Running (in two terminals)

```bash
# Terminal 1 - Backend
python -m sentinel.api.fastapi_bridge

# Terminal 2 - Frontend
cd gui && npm run dev

# Open: http://localhost:3000
```

## File Structure

```
✓ Backend Bridge: src/sentinel/api/fastapi_bridge.py (392 lines)
✓ Frontend: gui/ (complete React + TypeScript project)
✓ Documentation: docs/GUI_DEVELOPMENT.md (400+ lines)
✓ Setup Script: setup-gui.sh (automated installation)
```

## API Endpoints

| Method | Endpoint | Purpose |
|--------|----------|---------|
| GET | `/health` | Health check |
| GET | `/api/config` | Configuration |
| POST | `/api/scans` | Start scan |
| GET | `/api/scans/{id}` | Get results |
| WS | `/api/scans/{id}/progress` | Real-time updates |
| DELETE | `/api/scans/{id}` | Cancel scan |
| GET/PATCH | `/api/findings/{id}` | Finding details/update |
| POST | `/api/findings/{id}/notes` | Add notes |
| GET | `/api/projects` | Project history |

## Frontend Pages

| Page | Route | Purpose |
|------|-------|---------|
| Dashboard | `/` | Project selection & scan start |
| Results | `/results/:scanId` | Findings dashboard & details |

## Testing

```bash
# Health check
curl http://localhost:8000/health

# Start scan
curl -X POST http://localhost:8000/api/scans \
  -H "Content-Type: application/json" \
  -d '{"target_path": "./sample-project"}'
```

## Frontend Development

```bash
cd gui

npm run dev           # Start dev server
npm run type-check    # Type checking
npm run lint          # Linting
npm run build         # Production build
```

## Troubleshooting

| Issue | Solution |
|-------|----------|
| `ModuleNotFoundError: fastapi` | Run `pip install fastapi uvicorn` |
| `npm ERR!` | Run `cd gui && npm install` |
| CORS error | Ensure backend runs on 8000, frontend on 3000 |
| API not responding | Check `curl http://localhost:8000/health` |
| Hot reload not working | Restart dev server: `npm run dev` |

## Documentation

- **Full Guide**: [docs/GUI_DEVELOPMENT.md](docs/GUI_DEVELOPMENT.md)
- **Frontend README**: [gui/README.md](gui/README.md)
- **API Spec**: [docs/api/api-freeze-spec.md](docs/api/api-freeze-spec.md)
- **Implementation**: [PHASE3_IMPLEMENTATION.md](PHASE3_IMPLEMENTATION.md)

## Key Features ✨

✅ Project selection with validation  
✅ Real-time scan results  
✅ Severity filtering & breakdown  
✅ Finding details with AI explanations  
✅ Responsive 3-column layout  
✅ WebSocket for live updates  
✅ Type-safe TypeScript frontend  
✅ RESTful API design  
✅ Cross-platform (Windows/Mac/Linux)  

## What's Included

- **Backend**: FastAPI bridge (392 lines)
- **Frontend**: Complete React app with routing
- **Documentation**: 400+ lines of guides
- **Setup**: Automated installation script
- **Types**: Full TypeScript definitions
- **API**: 15 endpoints with error handling
- **Styling**: Professional CSS with responsive design

## Next Steps

1. ✅ Install dependencies: `./setup-gui.sh`
2. ✅ Start backend: `python -m sentinel.api.fastapi_bridge`
3. ✅ Start frontend: `cd gui && npm run dev`
4. ⏳ Test in browser: http://localhost:3000
5. ⏳ Try a scan: `./sample-project`

---

**Status**: Phase 3 GUI Foundation Complete 🎉  
**Version**: 0.2.0  
**Ready for**: Development & Testing
