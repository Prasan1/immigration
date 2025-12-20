"""
Team Management API Routes
"""
from flask import jsonify, request, session, render_template
from functools import wraps
from models import db, User
from team_models import Team, TeamMembership, TeamInvitation
from config import Config
import secrets
from datetime import datetime, timedelta

def login_required(f):
    """Simple login decorator"""
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if 'clerk_user_id' not in session:
            return jsonify({'error': 'Authentication required'}), 401
        return f(*args, **kwargs)
    return decorated_function

def get_current_user():
    """Get current user from session"""
    clerk_user_id = session.get('clerk_user_id')
    if clerk_user_id:
        return User.query.filter_by(clerk_user_id=clerk_user_id).first()
    return None

def register_team_routes(app):
    """Register all team-related routes"""

    @app.route('/team/dashboard')
    @login_required
    def team_dashboard():
        """Team management page"""
        user = get_current_user()
        if not user:
            return jsonify({'error': 'User not found'}), 404

        return render_template('team_management.html', user=user, config=Config)

    @app.route('/api/team/current', methods=['GET'])
    @login_required
    def get_current_team():
        """Get user's current active team"""
        user = get_current_user()
        if not user:
            return jsonify({'error': 'User not found'}), 404

        # Get user's active team or default to owned team
        team = None
        if hasattr(user, 'active_team_id') and user.active_team_id:
            team = Team.query.get(user.active_team_id)

        if not team:
            # Find first team user is member of
            membership = TeamMembership.query.filter_by(
                user_id=user.id,
                status='active'
            ).first()
            if membership:
                team = membership.team

        if not team:
            return jsonify({'error': 'No team found'}), 404

        # Get all members
        members = TeamMembership.query.filter_by(
            team_id=team.id,
            status='active'
        ).all()

        # Get pending invitations (only if user is owner/admin)
        invitations = []
        membership = TeamMembership.query.filter_by(
            team_id=team.id,
            user_id=user.id
        ).first()

        if membership and membership.role in ['owner', 'admin']:
            pending_invites = TeamInvitation.query.filter_by(
                team_id=team.id,
                status='pending'
            ).all()
            invitations = [inv.to_dict() for inv in pending_invites]

        return jsonify({
            'team': team.to_dict(),
            'members': [m.to_dict() for m in members],
            'invitations': invitations,
            'user_role': membership.role if membership else None,
            'can_invite': membership and membership.role in ['owner', 'admin'] and team.can_add_member()
        })

    @app.route('/api/team/invite', methods=['POST'])
    @login_required
    def invite_team_member():
        """Invite a new member to the team"""
        user = get_current_user()
        if not user:
            return jsonify({'error': 'User not found'}), 404

        data = request.json
        email = data.get('email', '').strip().lower()
        role = data.get('role', 'member')

        if not email:
            return jsonify({'error': 'Email is required'}), 400

        # Get user's active team
        if not hasattr(user, 'active_team_id') or not user.active_team_id:
            return jsonify({'error': 'No active team'}), 400

        team = Team.query.get(user.active_team_id)
        if not team:
            return jsonify({'error': 'Team not found'}), 404

        # Check if user has permission to invite
        membership = TeamMembership.query.filter_by(
            team_id=team.id,
            user_id=user.id
        ).first()

        if not membership or membership.role not in ['owner', 'admin']:
            return jsonify({'error': 'Permission denied'}), 403

        # Check if team has available seats
        if not team.can_add_member():
            return jsonify({
                'error': 'Team has reached maximum members',
                'max_seats': team.max_seats,
                'current_members': team.get_active_members_count(),
                'upgrade_message': 'Upgrade to Enterprise for unlimited team members'
            }), 400

        # Check if user is already a member
        existing_member = TeamMembership.query.join(User).filter(
            TeamMembership.team_id == team.id,
            User.email == email
        ).first()

        if existing_member:
            return jsonify({'error': 'User is already a team member'}), 400

        # Check if there's already a pending invitation
        existing_invite = TeamInvitation.query.filter_by(
            team_id=team.id,
            email=email,
            status='pending'
        ).first()

        if existing_invite:
            return jsonify({'error': 'Invitation already sent to this email'}), 400

        # Create invitation
        invitation = TeamInvitation(
            team_id=team.id,
            email=email,
            role=role,
            token=secrets.token_urlsafe(32),
            invited_by_id=user.id,
            expires_at=datetime.utcnow() + timedelta(days=7)  # 7 day expiry
        )

        db.session.add(invitation)
        db.session.commit()

        # TODO: Send invitation email here
        # send_invitation_email(email, invitation.token, team.name)

        return jsonify({
            'message': 'Invitation sent successfully',
            'invitation': invitation.to_dict(),
            'note': 'Email sending not yet implemented - user can sign up and accept invite'
        })

    @app.route('/api/team/invitations/pending', methods=['GET'])
    @login_required
    def get_user_invitations():
        """Get pending invitations for current user's email"""
        user = get_current_user()
        if not user:
            return jsonify({'error': 'User not found'}), 404

        invitations = TeamInvitation.query.filter_by(
            email=user.email,
            status='pending'
        ).all()

        return jsonify({
            'invitations': [{
                **inv.to_dict(),
                'team_name': inv.team.name,
                'invited_by_name': inv.invited_by.full_name or inv.invited_by.email
            } for inv in invitations if inv.is_valid()]
        })

    @app.route('/api/team/invitations/<int:invitation_id>/accept', methods=['POST'])
    @login_required
    def accept_invitation(invitation_id):
        """Accept a team invitation"""
        user = get_current_user()
        if not user:
            return jsonify({'error': 'User not found'}), 404

        invitation = TeamInvitation.query.get(invitation_id)
        if not invitation:
            return jsonify({'error': 'Invitation not found'}), 404

        # Verify invitation is for this user
        if invitation.email.lower() != user.email.lower():
            return jsonify({'error': 'This invitation is not for you'}), 403

        # Check if invitation is valid
        if not invitation.is_valid():
            return jsonify({'error': 'Invitation is expired or invalid'}), 400

        # Check if team has space
        team = invitation.team
        if not team.can_add_member():
            return jsonify({'error': 'Team has reached maximum members'}), 400

        # Check if already a member
        existing = TeamMembership.query.filter_by(
            team_id=team.id,
            user_id=user.id
        ).first()

        if existing:
            return jsonify({'error': 'You are already a member of this team'}), 400

        # Create membership
        membership = TeamMembership(
            team_id=team.id,
            user_id=user.id,
            role=invitation.role,
            status='active'
        )
        db.session.add(membership)

        # Update invitation
        invitation.status = 'accepted'
        invitation.accepted_at = datetime.utcnow()

        # Set as user's active team if they don't have one
        if not hasattr(user, 'active_team_id') or not user.active_team_id:
            user.active_team_id = team.id

        db.session.commit()

        return jsonify({
            'message': 'Successfully joined team',
            'team': team.to_dict(),
            'membership': membership.to_dict()
        })

    @app.route('/api/team/invitations/<int:invitation_id>/decline', methods=['POST'])
    @login_required
    def decline_invitation(invitation_id):
        """Decline a team invitation"""
        user = get_current_user()
        if not user:
            return jsonify({'error': 'User not found'}), 404

        invitation = TeamInvitation.query.get(invitation_id)
        if not invitation:
            return jsonify({'error': 'Invitation not found'}), 404

        if invitation.email.lower() != user.email.lower():
            return jsonify({'error': 'This invitation is not for you'}), 403

        invitation.status = 'declined'
        db.session.commit()

        return jsonify({'message': 'Invitation declined'})

    @app.route('/api/team/members/<int:membership_id>/remove', methods=['DELETE'])
    @login_required
    def remove_team_member(membership_id):
        """Remove a member from the team"""
        user = get_current_user()
        if not user:
            return jsonify({'error': 'User not found'}), 404

        membership = TeamMembership.query.get(membership_id)
        if not membership:
            return jsonify({'error': 'Membership not found'}), 404

        # Check permission
        user_membership = TeamMembership.query.filter_by(
            team_id=membership.team_id,
            user_id=user.id
        ).first()

        if not user_membership or user_membership.role not in ['owner', 'admin']:
            return jsonify({'error': 'Permission denied'}), 403

        # Can't remove the owner
        if membership.role == 'owner':
            return jsonify({'error': 'Cannot remove team owner'}), 400

        # Mark as removed instead of deleting
        membership.status = 'removed'
        db.session.commit()

        return jsonify({'message': 'Member removed successfully'})

    @app.route('/api/team/switch/<int:team_id>', methods=['POST'])
    @login_required
    def switch_active_team(team_id):
        """Switch user's active team"""
        user = get_current_user()
        if not user:
            return jsonify({'error': 'User not found'}), 404

        # Verify user is a member of this team
        membership = TeamMembership.query.filter_by(
            team_id=team_id,
            user_id=user.id,
            status='active'
        ).first()

        if not membership:
            return jsonify({'error': 'You are not a member of this team'}), 403

        user.active_team_id = team_id
        db.session.commit()

        return jsonify({
            'message': 'Active team switched',
            'team': membership.team.to_dict()
        })

    @app.route('/api/team/my-teams', methods=['GET'])
    @login_required
    def get_my_teams():
        """Get all teams user is a member of"""
        user = get_current_user()
        if not user:
            return jsonify({'error': 'User not found'}), 404

        memberships = TeamMembership.query.filter_by(
            user_id=user.id,
            status='active'
        ).all()

        teams = [{
            **m.team.to_dict(),
            'role': m.role,
            'is_active': m.team_id == (user.active_team_id if hasattr(user, 'active_team_id') else None)
        } for m in memberships]

        return jsonify({'teams': teams})
