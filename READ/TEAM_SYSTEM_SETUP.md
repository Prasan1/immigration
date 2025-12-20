# Multi-User Team System Implementation Guide

## Overview

This guide will help you implement the multi-user team system that enables:
- **Professional Plan**: Up to 3 team members
- **Enterprise Plan**: Unlimited team members
- Team invitations and management
- Role-based access control

---

## Step 1: Update app.py

Add these imports at the top of `app.py`:

```python
from team_models import Team, TeamMembership, TeamInvitation
from team_routes import register_team_routes
```

Then add this line AFTER creating the app (around line 24, after `app = create_app()`):

```python
# Register team routes
register_team_routes(app)
```

Add a new route for the team management page (around line 130):

```python
@app.route('/team')
@login_required
def team_management():
    user = get_current_user()
    return render_template('team_management.html', user=user)
```

---

## Step 2: Update models.py

Add this column to the `User` model in `models.py` (around line 23):

```python
# Add after the subscription fields
active_team_id = db.Column(db.Integer, db.ForeignKey('teams.id'))
```

Add relationship at the end of User class:

```python
# Add near the end of User class
active_team = db.relationship('Team', foreign_keys=[active_team_id])
```

---

## Step 3: Run Database Migration

Run the migration script to create team tables and migrate existing users:

```bash
source .venv/bin/activate
python3 migrate_teams.py
```

This will:
- Create 3 new tables: `teams`, `team_memberships`, `team_invitations`
- Create a personal team for each existing user
- Add `active_team_id` column to users table

---

## Step 4: Update Stripe Webhook (Optional)

To ensure team seats update when subscription changes, update your Stripe webhook handler in `app.py`:

Find the `stripe_webhook()` function (around line 315) and add this after updating the user's subscription:

```python
# After updating user subscription (around line 345)
# Update user's team if they own one
owned_team = Team.query.filter_by(owner_id=user.id).first()
if owned_team:
    owned_team.update_from_subscription(user)
```

---

## Step 5: Update Dashboard Navigation

Add a link to team management in your dashboard or navigation. In `templates/dashboard.html`, add:

```html
<a href="/team" class="nav-link">
    <i class="fas fa-users me-2"></i>Team Management
</a>
```

---

## Step 6: Update Access Control (Important!)

To make team members inherit the owner's subscription benefits, update the `get_current_user()` function in `app.py`:

Replace the existing function (around line 55) with:

```python
def get_current_user():
    """Get current user from session with team context"""
    clerk_user_id = session.get('clerk_user_id')
    if not clerk_user_id:
        return None

    user = User.query.filter_by(clerk_user_id=clerk_user_id).first()
    if not user:
        return None

    # If user has an active team, inherit team's subscription
    if hasattr(user, 'active_team_id') and user.active_team_id:
        team = Team.query.get(user.active_team_id)
        if team and team.subscription_status == 'active':
            # Create a virtual user object with team's subscription
            user._team_subscription_tier = team.subscription_tier
            user._team_subscription_status = team.subscription_status

            # Override user's subscription methods
            original_tier = user.subscription_tier
            original_status = user.subscription_status
            user.subscription_tier = team.subscription_tier
            user.subscription_status = team.subscription_status

    return user
```

---

## Step 7: Testing the System

### Test Professional Plan (3 users):

1. **Create a Professional subscription**:
   ```bash
   # In Python shell or create via Stripe checkout
   python3
   >>> from app import app
   >>> from models import db, User
   >>> from team_models import Team
   >>>
   >>> with app.app_context():
   ...     user = User.query.filter_by(email='owner@test.com').first()
   ...     user.subscription_tier = 'pro'
   ...     user.subscription_status = 'active'
   ...     db.session.commit()
   ...
   ...     team = Team.query.filter_by(owner_id=user.id).first()
   ...     team.update_from_subscription(user)
   ```

2. **Login as owner** and go to `/team`
3. **Invite 2 members** (total 3 users allowed)
4. **Try inviting a 4th user** - should get "Team has reached maximum members" error

### Test Enterprise Plan (unlimited):

1. **Upgrade to Enterprise**:
   ```python
   user.subscription_tier = 'enterprise'
   team.update_from_subscription(user)
   ```

2. **Invite unlimited members** - should work without limit

### Test Team Member Access:

1. **Invited member signs up** with the email they were invited with
2. **After login**, member goes to `/team` or checks `/api/team/invitations/pending`
3. **Accept invitation** - member now has access to team's subscription features
4. **Team member** can access forms based on team owner's subscription tier

---

## API Endpoints Reference

### Team Management
- `GET /api/team/current` - Get current team info and members
- `GET /api/team/my-teams` - Get all teams user is member of
- `POST /api/team/switch/{team_id}` - Switch active team

### Invitations
- `POST /api/team/invite` - Invite new member (owner/admin only)
  ```json
  { "email": "user@example.com", "role": "member" }
  ```
- `GET /api/team/invitations/pending` - Get user's pending invitations
- `POST /api/team/invitations/{id}/accept` - Accept invitation
- `POST /api/team/invitations/{id}/decline` - Decline invitation

### Members
- `DELETE /api/team/members/{id}/remove` - Remove member (owner only)

---

## Database Schema

### teams
- `id` - Primary key
- `name` - Team name
- `owner_id` - Foreign key to users
- `subscription_tier` - free/basic/pro/enterprise
- `subscription_status` - active/inactive
- `max_seats` - 1 for free/basic, 3 for pro, -1 for enterprise
- Timestamps

### team_memberships
- `id` - Primary key
- `team_id` - Foreign key to teams
- `user_id` - Foreign key to users
- `role` - owner/admin/member
- `status` - active/suspended/removed
- Timestamps

### team_invitations
- `id` - Primary key
- `team_id` - Foreign key to teams
- `email` - Invitee email
- `token` - Secure invitation token
- `role` - Intended role
- `status` - pending/accepted/expired/revoked
- `invited_by_id` - Foreign key to users
- Expires after 7 days

---

## Seat Limits by Tier

| Tier | Max Seats | Description |
|------|-----------|-------------|
| Free | 1 | Personal use only |
| Basic | 1 | Personal use only |
| Professional | 3 | Small teams |
| Enterprise | Unlimited | Large organizations |

---

## Security Considerations

1. **Email Verification**: Currently, invitations are stored but emails are not sent. To enable email sending:
   - Set up SMTP configuration
   - Implement `send_invitation_email()` function
   - Add email verification

2. **Token Security**: Invitation tokens are 32-byte URL-safe strings generated with `secrets.token_urlsafe()`

3. **Permission Checks**: All team operations verify user's role before allowing actions

4. **Invitation Expiry**: Invitations automatically expire after 7 days

---

## Future Enhancements

Consider adding:
1. **Email notifications** for invitations
2. **Team switching UI** in navbar dropdown
3. **Audit logs** for team actions
4. **Custom permissions** per member
5. **Team analytics** dashboard
6. **Bulk member import** for Enterprise
7. **SSO integration** for Enterprise

---

## Troubleshooting

### "No team found" error
- Ensure migration ran successfully
- Check that user has `active_team_id` set
- Verify team exists in database

### Members can't access premium forms
- Ensure team's `subscription_tier` matches owner's tier
- Check `get_current_user()` function inherits team subscription
- Verify `subscription_status` is 'active'

### Can't invite more members
- Check current member count: `team.get_active_members_count()`
- Verify `max_seats` matches subscription tier
- For Pro: max 3 total (including owner)
- For Enterprise: should be -1 (unlimited)

### Invitation not showing up
- Check invitation status: should be 'pending'
- Verify email matches exactly (case-insensitive)
- Check expiry: invitations expire after 7 days

---

## Support

For issues or questions:
1. Check database with: `python3 -c "from app import app; from team_models import *; # run queries"`
2. Review logs for error messages
3. Verify subscription tier matches expected seat limits

---

## Summary

You now have a complete multi-user team system with:
- ✅ Professional plans supporting 3 team members
- ✅ Enterprise plans supporting unlimited members
- ✅ Team invitations with secure tokens
- ✅ Role-based access control (owner/admin/member)
- ✅ Dashboard for team management
- ✅ Automatic seat limit enforcement
- ✅ Team members inheriting owner's subscription benefits
