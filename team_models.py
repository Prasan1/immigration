"""
Team and Multi-User Models
Supports Professional (3 users) and Enterprise (unlimited) tiers
"""
from models import db
from datetime import datetime
from sqlalchemy import UniqueConstraint

class Team(db.Model):
    """Organization/Team that owns the subscription"""
    __tablename__ = 'teams'

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(255), nullable=False)

    # Owner is the user who created the team and manages billing
    owner_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)

    # Subscription info (copied from owner's subscription)
    subscription_tier = db.Column(db.String(50), default='free')
    subscription_status = db.Column(db.String(50), default='inactive')
    stripe_subscription_id = db.Column(db.String(255))

    # Seat limits based on tier
    max_seats = db.Column(db.Integer, default=1)  # 1 for free, 3 for pro, unlimited (-1) for enterprise

    # Timestamps
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    # Relationships
    owner = db.relationship('User', foreign_keys=[owner_id], backref='owned_teams')
    members = db.relationship('TeamMembership', back_populates='team', cascade='all, delete-orphan')
    invitations = db.relationship('TeamInvitation', back_populates='team', cascade='all, delete-orphan')

    def __repr__(self):
        return f'<Team {self.name}>'

    def get_active_members_count(self):
        """Get count of active members"""
        return TeamMembership.query.filter_by(
            team_id=self.id,
            status='active'
        ).count()

    def can_add_member(self):
        """Check if team can add more members"""
        if self.max_seats == -1:  # Unlimited (enterprise)
            return True
        return self.get_active_members_count() < self.max_seats

    def get_available_seats(self):
        """Get number of available seats"""
        if self.max_seats == -1:
            return 'Unlimited'
        return self.max_seats - self.get_active_members_count()

    def update_from_subscription(self, user):
        """Update team limits based on user's subscription"""
        from config import Config

        self.subscription_tier = user.subscription_tier
        self.subscription_status = user.subscription_status
        self.stripe_subscription_id = user.stripe_subscription_id

        # Set max_seats based on tier configuration
        tier_config = Config.SUBSCRIPTION_TIERS.get(user.subscription_tier, {})
        self.max_seats = tier_config.get('max_users', 1)
        db.session.commit()

    def to_dict(self):
        return {
            'id': self.id,
            'name': self.name,
            'owner_id': self.owner_id,
            'subscription_tier': self.subscription_tier,
            'subscription_status': self.subscription_status,
            'max_seats': self.max_seats,
            'active_members': self.get_active_members_count(),
            'available_seats': self.get_available_seats(),
            'created_at': self.created_at.isoformat()
        }


class TeamMembership(db.Model):
    """Users who are members of a team"""
    __tablename__ = 'team_memberships'
    __table_args__ = (
        UniqueConstraint('team_id', 'user_id', name='unique_team_user'),
    )

    id = db.Column(db.Integer, primary_key=True)
    team_id = db.Column(db.Integer, db.ForeignKey('teams.id'), nullable=False)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)

    # Role within the team
    role = db.Column(db.String(50), default='member')  # owner, admin, member

    # Status
    status = db.Column(db.String(50), default='active')  # active, suspended, removed

    # Timestamps
    joined_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    # Relationships
    team = db.relationship('Team', back_populates='members')
    user = db.relationship('User', backref='team_memberships')

    def __repr__(self):
        return f'<TeamMembership team={self.team_id} user={self.user_id}>'

    def to_dict(self):
        return {
            'id': self.id,
            'team_id': self.team_id,
            'user_id': self.user_id,
            'user_email': self.user.email if self.user else None,
            'user_name': self.user.full_name if self.user else None,
            'role': self.role,
            'status': self.status,
            'joined_at': self.joined_at.isoformat()
        }


class TeamInvitation(db.Model):
    """Pending invitations to join a team"""
    __tablename__ = 'team_invitations'

    id = db.Column(db.Integer, primary_key=True)
    team_id = db.Column(db.Integer, db.ForeignKey('teams.id'), nullable=False)

    # Invitation details
    email = db.Column(db.String(255), nullable=False)
    role = db.Column(db.String(50), default='member')

    # Invitation token for secure acceptance
    token = db.Column(db.String(255), unique=True, nullable=False)

    # Status
    status = db.Column(db.String(50), default='pending')  # pending, accepted, expired, revoked

    # Who sent the invitation
    invited_by_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)

    # Timestamps
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    expires_at = db.Column(db.DateTime)  # Optional expiry
    accepted_at = db.Column(db.DateTime)

    # Relationships
    team = db.relationship('Team', back_populates='invitations')
    invited_by = db.relationship('User', foreign_keys=[invited_by_id])

    def __repr__(self):
        return f'<TeamInvitation {self.email} to team {self.team_id}>'

    def is_valid(self):
        """Check if invitation is still valid"""
        if self.status != 'pending':
            return False
        if self.expires_at and self.expires_at < datetime.utcnow():
            self.status = 'expired'
            db.session.commit()
            return False
        return True

    def to_dict(self):
        return {
            'id': self.id,
            'team_id': self.team_id,
            'email': self.email,
            'role': self.role,
            'status': self.status,
            'invited_by': self.invited_by.full_name if self.invited_by else None,
            'created_at': self.created_at.isoformat(),
            'expires_at': self.expires_at.isoformat() if self.expires_at else None
        }
