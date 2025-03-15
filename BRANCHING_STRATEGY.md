# Git Branching Strategy

This document outlines the Git branching strategy for the TaxAI project.

## Branch Structure

We follow a simplified Git Flow approach with the following branches:

### Main Branches

- `main` - Production-ready code. All releases are tagged from this branch.
- `develop` - Main development branch. Feature branches are merged here after review.

### Supporting Branches

- `feature/*` - New features and non-emergency bugfixes (branched from `develop`)
- `hotfix/*` - Urgent production fixes (branched from `main`)
- `release/*` - Release preparation (branched from `develop`)

## Workflow

1. **Feature Development**
   - Create a new branch from `develop`: `feature/feature-name`
   - Develop and test the feature
   - Create a pull request to `develop`
   - After code review, merge into `develop`

2. **Release Process**
   - Create a release branch from `develop`: `release/vX.Y.Z`
   - Only bugfixes are allowed in release branches
   - When ready, merge into both `main` and `develop`
   - Tag the release in `main`

3. **Hotfix Process**
   - Create a hotfix branch from `main`: `hotfix/vX.Y.Z`
   - Fix the critical issue
   - Create a pull request to both `main` and `develop`
   - After code review, merge into both branches
   - Tag the hotfix in `main`

## Commit Message Guidelines

Follow conventional commits format:

- `feat`: A new feature
- `fix`: A bug fix
- `docs`: Documentation changes
- `style`: Code style changes (formatting, etc.)
- `refactor`: Code changes that neither fix bugs nor add features
- `test`: Adding or modifying tests
- `chore`: Changes to the build process or auxiliary tools

Example: `feat(auth): implement JWT token authentication`

## Branch Naming Conventions

- Feature branches: `feature/short-description`
- Hotfix branches: `hotfix/vX.Y.Z` or `hotfix/issue-description`
- Release branches: `release/vX.Y.Z`

## Git Commands Quick Reference

```bash
# Create a new feature branch
git checkout develop
git pull
git checkout -b feature/new-feature

# Create a hotfix branch
git checkout main
git pull
git checkout -b hotfix/critical-fix

# Create a release branch
git checkout develop
git pull
git checkout -b release/v1.0.0
```
