# AGENT_CONTEXT.md — Repository Onboarding for AI Agents

> This file tells AI agents how to work in this repository.
> Place this file in the ROOT of your project.

## Project Overview
- **Name:** User Management Service
- **Language:** Java 17
- **Framework:** Spring Boot 3.x
- **Build Tool:** Maven
- **Database:** PostgreSQL with Spring Data JPA / Hibernate

## Build & Test Commands
```bash
# Compile the project
mvn clean compile

# Run all tests
mvn test

# Run a specific test class
mvn test -Dtest=ClassName

# Package the application
mvn clean package -DskipTests
```

## Project Structure
```
src/
├── main/java/dev/rahul/usermanagement/
│   ├── controllers/       # REST controllers (@RestController)
│   ├── services/           # Business logic (@Service)
│   ├── repositories/       # JPA repositories (@Repository)
│   ├── models/             # JPA entities (@Entity)
│   ├── dto/                # Request/Response DTOs
│   ├── config/             # Spring configuration classes
│   └── exceptions/         # Custom exception classes
├── main/resources/
│   ├── application.yml     # App configuration
│   └── db/migration/       # Flyway migration scripts
└── test/java/dev/rahul/usermanagement/
    ├── controllers/        # Controller tests (MockMvc)
    └── services/           # Service unit tests (Mockito)
```

## Coding Standards & Rules
1. **Naming:** Use camelCase for variables/methods, PascalCase for classes.
2. **Annotations:** Always use constructor injection (not field injection with @Autowired).
3. **DTOs:** Never return JPA entities directly from controllers. Always map to DTOs.
4. **Logging:** Use SLF4J (`@Slf4j` from Lombok). Never use `System.out.println`.
5. **Exceptions:** Throw custom exceptions (e.g., `ResourceNotFoundException`) and handle them in a `@ControllerAdvice` class.
6. **Tests:** Use JUnit 5 with Mockito for service tests and MockMvc for controller tests.
7. **Database:** Use Flyway for migrations. Never alter tables with JPA auto-DDL in production.

## Dependencies Already Available
- Spring Web, Spring Data JPA, Spring Security
- Lombok
- BCryptPasswordEncoder (from Spring Security)
- Flyway (for database migrations)
- JUnit 5, Mockito, MockMvc (for testing)
