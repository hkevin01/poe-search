# System Design

## Architecture Overview

Poe Search follows a modular architecture with clear separation of concerns:

```
┌─────────────────┐
│   GUI Layer     │  ← PyQt6 Interface
├─────────────────┤
│ Services Layer  │  ← Business Logic
├─────────────────┤
│   API Layer     │  ← External Integrations
├─────────────────┤
│  Models Layer   │  ← Data Models
└─────────────────┘
```

## Component Interaction

1. **GUI Layer** - User interface using PyQt6
2. **Services Layer** - Business logic (export, search, sync)
3. **API Layer** - Browser automation and external APIs
4. **Models Layer** - Data models and validation

## Data Flow

1. User initiates action in GUI
2. GUI calls appropriate service
3. Service uses API clients for data
4. Data flows back through layers
5. GUI updates with results

## Key Design Patterns

- **Repository Pattern** - Data access abstraction
- **Service Layer Pattern** - Business logic separation
- **Observer Pattern** - GUI updates and progress tracking
- **Factory Pattern** - Object creation and configuration
