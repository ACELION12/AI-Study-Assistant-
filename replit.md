# AI Study Assistant

## Overview

AI Study Assistant is a Streamlit-based educational application that provides intelligent tutoring support through AI-powered conversations. The system helps students by answering questions across multiple subjects, categorizing queries by academic discipline, and maintaining comprehensive study session records. Built with Streamlit for the web interface and Groq for AI responses, it features persistent storage of study sessions and chat exchanges with rating capabilities for continuous improvement.

## User Preferences

Preferred communication style: Simple, everyday language.

## System Architecture

### Frontend Architecture
- **Streamlit Web Framework**: Single-page application with wide layout configuration for optimal user experience
- **Session State Management**: Utilizes Streamlit's built-in session state for maintaining conversation context and user interactions
- **Real-time Chat Interface**: Provides immediate AI responses with conversation history display

### Backend Architecture
- **SQLAlchemy ORM**: Database abstraction layer using declarative base pattern for clean data modeling
- **Session-based Database Access**: Factory pattern implementation for database connections with proper session management
- **Modular Service Architecture**: Separated concerns with dedicated modules for database operations, subject categorization, and AI integration

### AI Integration
- **Groq API Client**: External AI service integration with caching for performance optimization
- **Subject-Aware Prompting**: Enhanced response generation using subject-specific context and educational focus
- **Conversation Context**: Maintains chat history for improved response relevance and continuity

### Data Models
- **Study Sessions**: Container entities for organizing related conversations with timestamp tracking
- **Chat Exchanges**: Individual question-answer pairs with subject categorization, user ratings, and feedback storage
- **Rating System**: Both numerical (1-5) and binary (thumbs up/down) feedback mechanisms for response quality assessment

### Subject Categorization System
- **Keyword-based Classification**: Automatic subject detection using predefined keyword dictionaries across 8 academic disciplines
- **Enhanced Prompting**: Subject-specific system prompts for more accurate and contextually appropriate responses
- **Multi-domain Support**: Covers Mathematics, Science, History, Geography, Literature, Computer Science, Language Arts, and Social Studies

## External Dependencies

### AI Services
- **Groq API**: Primary AI service for generating educational responses, requires GROQ_API_KEY environment variable

### Database
- **SQLAlchemy**: Object-relational mapping and database abstraction
- **Database Engine**: Configurable via DATABASE_URL environment variable (supports PostgreSQL, MySQL, SQLite)

### Web Framework
- **Streamlit**: Complete web application framework handling UI rendering, session management, and user interactions

### Python Libraries
- **datetime**: Built-in library for timestamp management and session tracking
- **os**: Environment variable access for configuration management
- **re**: Regular expression support for text processing in subject categorization
- **typing**: Type hints for improved code documentation and IDE support
- **json**: Data serialization for complex data structures
- **io**: Input/output operations for data handling

### Environment Configuration
- **GROQ_API_KEY**: Required environment variable for AI service authentication
- **DATABASE_URL**: Required environment variable for database connection configuration