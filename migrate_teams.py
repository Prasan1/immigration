#!/usr/bin/env python3
"""
Migration script to add team/multi-user tables and update existing users
"""
from app import app
from models import db, User
from team_models import Team, TeamMembership, TeamInvitation
import secrets

def migrate_teams():
    """Create team tables and migrate existing users"""

    with app.app_context():
        # Create team tables
        db.create_all()
        print("✓ Created team tables (teams, team_memberships, team_invitations)")

        # Add active_team_id to users table if it doesn't exist
        # This tracks which team the user is currently viewing
        try:
            db.session.execute(db.text('ALTER TABLE users ADD COLUMN active_team_id INTEGER REFERENCES teams(id)'))
            db.session.commit()
            print("✓ Added active_team_id column to users table")
        except Exception as e:
            if 'already exists' in str(e) or 'duplicate column' in str(e).lower():
                print("⚠️  active_team_id column already exists")
                db.session.rollback()
            else:
                print(f"❌ Error adding column: {e}")
                db.session.rollback()
                return

        # Migrate existing users to have their own personal team
        users = User.query.all()
        migrated_count = 0

        for user in users:
            # Check if user already has a team
            existing_team = Team.query.filter_by(owner_id=user.id).first()
            if existing_team:
                print(f"⚠️  User {user.email} already has a team, skipping...")
                continue

            # Create personal team for the user
            team = Team(
                name=f"{user.full_name or user.email}'s Team",
                owner_id=user.id,
                subscription_tier=user.subscription_tier,
                subscription_status=user.subscription_status,
                stripe_subscription_id=user.stripe_subscription_id
            )

            # Set max_seats based on tier
            tier_seats = {
                'free': 1,
                'basic': 1,
                'pro': 3,
                'enterprise': -1  # unlimited
            }
            team.max_seats = tier_seats.get(user.subscription_tier, 1)

            db.session.add(team)
            db.session.flush()  # Get the team.id

            # Add user as owner member
            membership = TeamMembership(
                team_id=team.id,
                user_id=user.id,
                role='owner',
                status='active'
            )
            db.session.add(membership)

            # Set as active team
            user.active_team_id = team.id

            migrated_count += 1

        db.session.commit()
        print(f"\n✓ Successfully migrated {migrated_count} users to teams")

        # Show summary
        total_teams = Team.query.count()
        total_memberships = TeamMembership.query.count()

        print(f"\n📊 Summary:")
        print(f"  - Total teams: {total_teams}")
        print(f"  - Total memberships: {total_memberships}")
        print(f"  - Total users: {User.query.count()}")

        print("\n✅ Team migration complete!")
        print("\nNext steps:")
        print("1. Restart your Flask application")
        print("2. Users can now invite team members from their dashboard")
        print("3. Professional plans can add up to 3 total users")
        print("4. Enterprise plans can add unlimited users")

if __name__ == '__main__':
    migrate_teams()
