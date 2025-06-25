you # DADM Release Procedure

This document outlines the complete procedure for creating and deploying DADM releases, including version management, documentation, git workflow, and deployment considerations.

## Overview

DADM follows semantic versioning (SemVer) with a structured release process that includes:
- Version bumping
- Comprehensive documentation updates
- Git workflow with tagging and branching
- Release validation and deployment

## Prerequisites

### Required Tools
- Git with push access to the DADM repository
- Node.js 18+ for UI development and testing
- Docker and Docker Compose for container management
- PM2 for process management
- Access to production deployment environments

### Required Permissions
- Write access to the main DADM repository
- Ability to create tags and release branches
- Access to CI/CD pipeline (if applicable)
- Production deployment credentials

## Release Workflow

### 1. Pre-Release Preparation

#### 1.1 Feature Branch Completion
Ensure all features for the release are complete and merged into a feature branch:

```bash
# Verify current branch has all intended changes
git status
git log --oneline -10

# Ensure all changes are committed
git add .
git commit -m "feat: [Description of final changes]"
```

#### 1.2 Testing and Validation
Before starting the release process, ensure:
- [ ] All new features are thoroughly tested
- [ ] UI components render correctly
- [ ] Backend APIs respond properly
- [ ] Database integration works correctly
- [ ] Docker containers start successfully
- [ ] No critical bugs or regressions

### 2. Version Management

#### 2.1 Determine Version Number
Follow semantic versioning:
- **Major (X.0.0)**: Breaking changes, major new features
- **Minor (X.Y.0)**: New features, backward compatible
- **Patch (X.Y.Z)**: Bug fixes, backward compatible

#### 2.2 Update Version Number
Update the version in `/scripts/__init__.py`:

```python
# Before
__version__ = "0.11.0"

# After (example for patch release)
__version__ = "0.11.1"
```

### 3. Documentation Updates

#### 3.1 Update Changelog
Edit `/changelog.md` to add the new release section:

```markdown
## [Unreleased]

## [0.11.1] - 2025-06-18

### Added
- List of new features and capabilities
- New API endpoints or UI components
- Enhanced functionality descriptions

### Enhanced
- Improvements to existing features
- Performance optimizations
- User experience enhancements

### Fixed
- Bug fixes and issue resolutions
- Database integration fixes
- UI stability improvements
```

#### 3.2 Create Release Summary
Create a new file `/RELEASE_v[VERSION]_SUMMARY.md`:

```markdown
# DADM Release v0.11.1 Summary

**Release Date:** [Date]
**Version:** [Version]
**Theme:** [Release Theme]

## 🎯 Key Achievements
- Major feature implementations
- Technical improvements
- User experience enhancements

## 📊 Impact Metrics
| Component | Before | After | Improvement |
|-----------|--------|-------|-------------|
| [Feature] | [Old] | [New] | ✅ [Improvement] |

## 🚀 User Experience Improvements
### For [User Type]
- Benefit descriptions
- New capabilities
- Workflow improvements
```

#### 3.3 Create Release Notes
Create a new file `/release_notes_v[VERSION].md`:

```markdown
# Release Notes - DADM v0.11.1

**Release Date:** [Date]
**Version:** [Version]

## 🌟 What's New
### [Feature Category]
- Detailed feature descriptions
- User-facing improvements
- Technical enhancements

## 🐛 Bug Fixes
- List of resolved issues
- Stability improvements
- Performance fixes

## 📋 Migration Guide
### From v[PREVIOUS] to v[CURRENT]
- Required changes
- Configuration updates
- Database migrations (if any)
```

### 4. Git Workflow

#### 4.1 Commit Release Documentation
```bash
# Add all documentation changes
git add .
git commit -m "feat: Release v[VERSION] - [Brief description of major features]"
```

#### 4.2 Merge to Main Branch
```bash
# Switch to main and ensure it's up to date
git checkout main
git pull origin main

# Merge the feature branch
git merge [feature-branch-name]

# Push merged changes to main
git push origin main
```

#### 4.3 Create Release Tag
```bash
# Create annotated tag with release message
git tag -a v[VERSION] -m "Release v[VERSION]: [Title]

- [Major feature 1]
- [Major feature 2]
- [Bug fixes and improvements]
- [Technical enhancements]"

# Push tag to remote
git push origin v[VERSION]
```

#### 4.4 Create Release Branch
```bash
# Create and switch to release branch
git checkout -b release/v[VERSION]

# Push release branch to remote
git push origin release/v[VERSION]
```

### 5. Release Validation

#### 5.1 Verify Git State
```bash
# Confirm branches and tags
git branch -a | grep -E "(main|release|v[VERSION])"
git tag | grep v[VERSION]

# Verify latest commits
git log --oneline -5
```

#### 5.2 Test Release Build
```bash
# Test backend services
cd /home/jdehart/dadm
pm2 status

# Test UI build (if applicable)
cd ui
npm install
npm run build

# Test Docker containers
docker ps
docker-compose -f docker/docker-compose.yml ps
```

### 6. Deployment

#### 6.1 Production Deployment Checklist
- [ ] Backup current production database
- [ ] Stop production services gracefully
- [ ] Deploy new version to staging environment
- [ ] Run regression tests on staging
- [ ] Deploy to production environment
- [ ] Verify all services start correctly
- [ ] Run post-deployment health checks
- [ ] Monitor logs for errors

#### 6.2 Rollback Plan
Prepare rollback procedures in case of deployment issues:
```bash
# Quick rollback to previous tag
git checkout v[PREVIOUS_VERSION]

# Restore previous Docker images
docker-compose -f docker/docker-compose.yml down
docker-compose -f docker/docker-compose.yml up -d

# Restore database backup (if needed)
# [Database-specific restore commands]
```

## Release Templates

### Feature Branch Commit Message
```
feat: [Brief description of feature]

- Detailed bullet point of changes
- Another significant change
- Technical implementation notes

Fixes: #[issue-number] (if applicable)
```

### Release Commit Message
```
feat: Release v[VERSION] - [Title describing main theme]

Major Features:
- [Feature 1 with brief description]
- [Feature 2 with brief description]
- [Feature 3 with brief description]

Improvements:
- [Improvement 1]
- [Improvement 2]

Bug Fixes:
- [Fix 1]
- [Fix 2]

Technical:
- [Technical change 1]
- [Technical change 2]
```

### Release Tag Message
```
Release v[VERSION]: [Title]

- [Major feature 1]
- [Major feature 2]
- [Significant improvements]
- [Critical bug fixes]
```

## Post-Release Activities

### 1. Communication
- [ ] Update team on release completion
- [ ] Notify stakeholders of new features
- [ ] Update documentation website (if applicable)
- [ ] Announce release in relevant channels

### 2. Monitoring
- [ ] Monitor production logs for 24-48 hours
- [ ] Track key performance metrics
- [ ] Monitor user feedback and bug reports
- [ ] Verify analytics and usage patterns

### 3. Follow-up
- [ ] Create GitHub release from tag (if using GitHub)
- [ ] Update project roadmap
- [ ] Plan next release cycle
- [ ] Document lessons learned

## Emergency Procedures

### Hotfix Release Process
For critical bugs requiring immediate release:

1. Create hotfix branch from main: `git checkout -b hotfix/v[VERSION]`
2. Apply minimal fix with tests
3. Update version to patch increment
4. Follow abbreviated documentation process
5. Fast-track through testing
6. Deploy with priority monitoring

### Release Rollback
If major issues are discovered post-release:

1. Immediately revert to previous stable tag
2. Restore database backups if schema changed
3. Communicate rollback to all stakeholders
4. Create incident report
5. Plan fix and re-release strategy

## Tools and Scripts

### Version Bump Script (Optional)
```bash
#!/bin/bash
# bump-version.sh
OLD_VERSION=$(grep "__version__" scripts/__init__.py | cut -d'"' -f2)
NEW_VERSION=$1

if [ -z "$NEW_VERSION" ]; then
    echo "Usage: ./bump-version.sh <new-version>"
    exit 1
fi

sed -i "s/__version__ = \"$OLD_VERSION\"/__version__ = \"$NEW_VERSION\"/" scripts/__init__.py
echo "Version bumped from $OLD_VERSION to $NEW_VERSION"
```

### Release Validation Script (Optional)
```bash
#!/bin/bash
# validate-release.sh
echo "Validating release readiness..."

# Check git status
if [ -n "$(git status --porcelain)" ]; then
    echo "❌ Uncommitted changes detected"
    exit 1
fi

# Check version consistency
VERSION=$(grep "__version__" scripts/__init__.py | cut -d'"' -f2)
if ! git tag | grep -q "v$VERSION"; then
    echo "✅ Version $VERSION ready for tagging"
else
    echo "❌ Version $VERSION already tagged"
    exit 1
fi

echo "✅ Release validation passed"
```

## Release Checklist Template

Copy this checklist for each release:

### Pre-Release
- [ ] All features tested and working
- [ ] Version number updated in scripts/__init__.py
- [ ] Changelog updated with new version section
- [ ] Release summary document created
- [ ] Release notes document created
- [ ] All changes committed to feature branch

### Git Workflow
- [ ] Feature branch merged to main
- [ ] Changes pushed to origin/main
- [ ] Release tag created and pushed
- [ ] Release branch created and pushed
- [ ] Git state verified (branches, tags, commits)

### Validation
- [ ] Backend services tested
- [ ] UI components working
- [ ] Docker containers healthy
- [ ] Database integration verified
- [ ] Documentation reviewed

### Deployment
- [ ] Production backup completed
- [ ] Staging deployment successful
- [ ] Production deployment completed
- [ ] Post-deployment health checks passed
- [ ] Monitoring alerts configured

### Post-Release
- [ ] Team and stakeholders notified
- [ ] Production monitoring active
- [ ] User feedback channels monitored
- [ ] Release retrospective scheduled

---

**Document Version:** 1.0  
**Last Updated:** June 18, 2025  
**Next Review:** Next major release

For questions or improvements to this procedure, please create an issue or submit a pull request.
