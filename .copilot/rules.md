# Poe Search Project - Copilot Rules

## Core Development Rules

### 1. **STRICT No Fake Data Policy - ABSOLUTE RULE**
- **NEVER EVER** create, insert, populate, or use fake/dummy/placeholder/sample data in ANY context
- **PROHIBITED**: Creating mock conversations, sample users, test data, or placeholder content
- **REQUIRED**: Always use real data from the actual Poe.com conversations that exist in the database
- If real data is not available, use empty states or proper error handling - NOT fake data
- When testing, use actual database queries against real existing conversation data
- When debugging, verify what real data actually exists rather than assuming or creating test data
- **VIOLATION EXAMPLES TO AVOID**: "Let's create some sample conversations", "I'll add test data", "Here's mock data for testing"

### 2. **Database Integrity**
- Always verify database paths and connections before assuming data exists
- Use the correct database file (`data/poe_search.db`) consistently
- Log database paths and connection status for debugging
- Never assume database content - always check and log actual counts/results

### 3. **Authentication & Security**
- Handle Poe.com tokens securely and validate them properly
- Use real browser session extraction for Poe-Formkey when possible
- Implement proper error handling for authentication failures
- Never hardcode or expose authentication credentials

### 4. **Error Handling & Logging**
- Provide detailed logging for all database operations
- Log actual file paths, existence checks, and operation results
- Use specific error messages that help diagnose real issues
- Always include context about what was attempted and what actually happened

### 5. **GUI Development**
- Ensure SearchWidget shows actual conversation data from the database
- Implement proper empty states when no data is available
- Use real conversation titles, dates, and content in the interface
- Test with actual Poe.com conversation data, not mock data

### 6. **Testing Philosophy**
- Tests should use real data from the project's database files
- Verify actual functionality against real Poe.com data structures
- Create integration tests that work with the actual Poe.com API
- Use real browser automation for token extraction testing

### 7. **Code Quality**
- Follow existing project structure and naming conventions
- Maintain compatibility with the existing PoeSearchClient architecture
- Use proper Python typing and error handling patterns
- Keep database operations consistent with the established Database class

### 8. **Debugging Approach**
- When debugging, always verify what data actually exists
- Check file paths, database contents, and API responses with real queries
- Use logging to trace actual data flow through the application
- Never assume expected behavior - always verify actual behavior

### 9. **Current Debugging Context (GUI Database Issue)**
- The GUI SearchWidget shows 0 conversations despite `data/poe_search.db` containing 4 real conversations
- Real conversation titles: "Python Web Development Discussion", "JavaScript React Tutorial", "Database Design Best Practices", "Machine Learning Introduction"
- Created on 2025-07-03, these are actual Poe.com conversations, not test data
- Focus on fixing the database connection/path issue, not creating workarounds with fake data
- MainWindow database initialization logs are missing - investigate why the Database object isn't connecting properly
- **SOLUTION APPROACH**: Debug the actual Database object being passed to SearchWidget, verify file paths, check connection integrity

## Project-Specific Context

### Database Structure
- Main database: `data/poe_search.db`
- Contains real Poe.com conversation data with fields: id, title, bot, created_at, updated_at, messages
- SearchWidget should display actual conversation titles and metadata

### Authentication Flow
- Uses Playwright for browser automation to extract tokens
- Handles Poe-Formkey validation and session management
- Implements fallback to manual token entry if browser extraction fails

### Architecture
- GUI built with PyQt6 with modular widget design
- Database layer uses SQLite with proper ORM-style queries
- API client handles real Poe.com GraphQL endpoints

## Development Priorities
1. Ensure actual conversation data displays in the GUI
2. Verify database connections and data integrity
3. Implement robust error handling for real-world scenarios
4. Maintain security and authentication best practices
5. Create tests that validate against real data structures
