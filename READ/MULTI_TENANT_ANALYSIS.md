# Multi-Tenant & Pricing Analysis

## Current Implementation Issues

### How Branding Works NOW (Broken for Teams):

**Code Evidence** (`app.py:42-53`):
```python
# Branding is tied to the LOGGED-IN USER only
user = get_current_user()
if user and user.subscription_tier == 'enterprise':
    settings = EnterpriseSettings.query.filter_by(user_id=user.id).first()
    # Shows THIS user's branding
```

### The Problem:

**ABC Law Firm Scenario:**
1. Partner John buys Enterprise ($199/month)
2. John sets up branding: "ABC Law Firm" logo, blue colors
3. John invites 19 team members (attorneys, paralegals)

**What happens when users log in:**
- ❌ **John logs in** → Sees "ABC Law Firm" branding ✓
- ❌ **Attorney Sarah logs in** → Sees DEFAULT branding (your branding) ✗
- ❌ **Paralegal Mike logs in** → Sees DEFAULT branding ✗

**Why?** Branding is tied to `user_id`, not `team_id`!

### Architecture Mismatch:

```
EnterpriseSettings
├── user_id (FK) ← Tied to ONE person
└── Branding data

Team
├── owner_id (FK) ← The paying customer
└── TeamMembership ← 20 members
    └── No connection to branding!
```

---

## Multi-Tenant Options

### Option 1: Subdomain Per Team (Common SaaS Model)
**URL Structure:**
- `abc-law.immigrationtemplates.com` ← ABC Law Firm
- `rodriguez-firm.immigrationtemplates.com` ← Rodriguez Firm
- `corporate-legal.immigrationtemplates.com` ← Corporate team

**How it works:**
1. Team owner sets up: Team Name = "ABC Law Firm"
2. System creates subdomain: `abc-law.immigrationtemplates.com`
3. All 20 team members access `abc-law.immigrationtemplates.com`
4. Branding applies based on subdomain, not user

**Pros:**
- ✅ Clean separation between organizations
- ✅ Easy to identify which org you're in
- ✅ Can set different branding per subdomain
- ✅ Team members bookmark their org's URL

**Cons:**
- ❌ Requires wildcard SSL certificate
- ❌ DNS configuration complexity
- ❌ Need subdomain routing in app

**Implementation Cost:** 2-3 days

---

### Option 2: Custom Domain Per Team (Premium)
**URL Structure:**
- `forms.abc-law.com` ← ABC Law Firm's own domain
- `immigration.rodriguezfirm.com` ← Rodriguez Firm's domain

**How it works:**
1. ABC Law Firm points their domain to your server
2. Your app detects domain and loads ABC's branding
3. All team members use `forms.abc-law.com`

**Pros:**
- ✅ Professional white-label experience
- ✅ Client never sees your brand
- ✅ Can charge premium ($299-$499/month)

**Cons:**
- ❌ Complex DNS setup per client
- ❌ Requires per-domain SSL
- ❌ Support overhead (clients mess up DNS)

**Implementation Cost:** 3-4 days

---

### Option 3: Team Context Switch (Simple Fix)
**URL Structure:**
- `immigrationtemplates.com` ← Everyone uses same domain
- Header shows: "ABC Law Firm" with logo
- Switch teams dropdown if member of multiple

**How it works:**
1. User logs in
2. App checks: "Which team(s) are you in?"
3. Loads branding from TEAM owner's settings
4. Header shows team name/logo
5. All 20 members see same "ABC Law Firm" branding

**Pros:**
- ✅ Simple to implement (4-6 hours)
- ✅ No infrastructure changes needed
- ✅ Works immediately
- ✅ Users can be in multiple teams

**Cons:**
- ❌ Same URL for everyone (less "white label")
- ❌ Clients might see other orgs if they switch teams

**Implementation Cost:** 4-6 hours

**Recommended for MVP:** ✅ YES - Start here

---

## Economics Analysis: $199 for 20 Users

### Cost Breakdown:

| Cost Item | Per User/Month | For 20 Users | Notes |
|-----------|----------------|--------------|-------|
| **Hosting (DB, Storage)** | $0.50 | $10 | Scales with storage |
| **Email service** | $0.10 | $2 | SendGrid/Mailgun |
| **Stripe fees (2.9%)** | $0.29 | $5.77 | On $199 revenue |
| **Support (avg)** | $3-5 | $60-100 | Biggest cost! |
| **Infrastructure** | $0.50 | $10 | CDN, backups |
| **Total Cost** | ~$4.50 | **$87.77** | |
| **Revenue** | | **$199** | |
| **Profit** | | **$111.23** | 56% margin |

### Per-User Economics:
- Revenue per user: **$9.95/month**
- Cost per user: **$4.39/month**
- Profit per user: **$5.56/month**

---

## Is $199 for 20 Users Profitable?

### Short Answer: MARGINALLY PROFITABLE

**Profit**: $111/month per team
**BUT** consider:
- Customer Acquisition Cost (CAC): $500-2000 for legal vertical
- Payback period: 4-18 months
- Churn risk: Law firms change vendors frequently

### The Math:
- $199/month × 12 months = **$2,388/year**
- Cost to acquire 1 customer: **$1,000** (ads, sales time)
- Annual profit: **$2,388 - $1,000 - ($88 × 12) = $332**
- **ROI: 17%** (not great, not terrible)

---

## Better Pricing Models

### Model 1: Per-Seat Pricing (Industry Standard)
```
Base: $49/month (1 user)
+$19/user/month for additional users

ABC Law Firm (20 users):
$49 + ($19 × 19) = $410/month
Annual: $4,920
Profit margin: 75%
```

**Pros:**
- ✅ Scales with value delivered
- ✅ Industry standard (everyone understands it)
- ✅ Higher revenue as teams grow

**Cons:**
- ❌ Harder to sell than "unlimited"
- ❌ Requires seat tracking

---

### Model 2: Tiered Unlimited (Your Current Approach)
```
Starter:        $29/month  (1 user, all forms)
Business:       $79/month  (3 users)
Enterprise:     $299/month (Unlimited users + white-label)
```

**Better pricing** than current $199:
- Unlimited users = premium feature
- Worth $299-499 for large firms
- $199 too cheap for 20+ users

**Pros:**
- ✅ Simple, predictable pricing
- ✅ "Unlimited" is compelling
- ✅ Easy to sell

**Cons:**
- ❌ Lose revenue on large teams
- ❌ Attracts low-paying, high-support customers

---

### Model 3: Hybrid (Recommended)
```
Professional:   $49/month   (Up to 5 users)
Business:       $149/month  (Up to 15 users)
Enterprise:     $299/month  (Up to 50 users + white-label)
Enterprise+:    $599/month  (Unlimited + white-label + custom domain)
```

**Why this works:**
- Captures small teams at $49
- Medium firms at $149 (sweet spot)
- Large firms at $299+ (better margin)
- "Up to X users" feels generous but sets limits

**Profit Margins:**
- Professional (5 users): 80% margin
- Business (15 users): 70% margin
- Enterprise (50 users): 65% margin

---

## Competitor Pricing (Immigration Software)

### LawLogix (Immigration Case Management):
- $150/user/month (enterprise)
- 20 users = **$3,000/month**

### Docketwise (Immigration Forms):
- $99/user/month
- 20 users = **$1,980/month**

### SimpleCitizen (Consumer Immigration):
- $1,199 one-time per application
- Not subscription-based

### YOUR PRICING: $199/month unlimited
- **10x cheaper than competitors!**
- Either raise prices OR limit users

---

## Multi-Tenant URLs: What Customers See

### Option A: Subdomain (Recommended)
**What ABC Law Firm employees see:**
1. They visit: `abc-law.immigrationtemplates.com`
2. Login page shows ABC Law Firm logo
3. All pages have ABC branding
4. Footer: "© 2025 ABC Law Firm" (if hide powered-by enabled)

**Perception:** Professional, branded experience

---

### Option B: Team Context (Simple)
**What ABC Law Firm employees see:**
1. They visit: `immigrationtemplates.com`
2. Login with their account
3. Header shows: "ABC Law Firm" logo and name
4. Dropdown: "ABC Law Firm" (can switch teams if in multiple)
5. Rest of site shows ABC branding

**Perception:** Good, but URL shows your brand

---

### Option C: Custom Domain (Premium)
**What ABC Law Firm employees see:**
1. They visit: `forms.abc-law.com` (their domain!)
2. 100% white-labeled
3. Never see your brand
4. Can have SSL cert in their name

**Perception:** Premium, looks like their own tool

---

## Recommendations

### For Production Launch:

1. **Fix branding immediately** (4-6 hours):
   - Change: `EnterpriseSettings.user_id` → `EnterpriseSettings.team_id`
   - Load branding from team owner, not logged-in user
   - All team members see same branding

2. **Use Team Context approach** (no subdomain needed):
   - Same URL for everyone
   - Header shows team branding
   - Simple, works today

3. **Raise Enterprise pricing**:
   - $199 → $299 (unlimited users + white-label)
   - Add $499 tier for custom domain

4. **Add seat limits**:
   - Business: $149/month (up to 10 users)
   - Enterprise: $299/month (up to 30 users)
   - Enterprise+: $499/month (unlimited)

### Long-term (After Launch):

1. **Add subdomain support** (2-3 days):
   - `teamname.immigrationtemplates.com`
   - Wildcard SSL
   - Better white-label experience

2. **Add per-seat pricing option**:
   - Let customers choose: Fixed or per-seat
   - Charge $25/user/month over limit

3. **Build usage analytics**:
   - Track which teams use it most
   - Identify upsell opportunities

---

## Profitability Summary

| Pricing Model | 5 Users | 10 Users | 20 Users | 50 Users | Profitable? |
|---------------|---------|----------|----------|----------|-------------|
| **Current: $199 flat** | $199 | $199 | $199 | $199 | ⚠️ Barely (20+) |
| **Per-seat: $49 + $19/user** | $125 | $220 | $410 | $980 | ✅ Yes |
| **Tiered: $149 (10), $299 (30)** | $149 | $149 | $299 | $299 | ✅ Yes |
| **Hybrid recommended** | $149 | $149 | $299 | $599 | ✅ Very |

**Conclusion:** Your current $199 unlimited is **underpriced** for teams over 10 people. You're essentially subsidizing large law firms.

---

## Action Items

### Critical (Before Launch):
- [ ] Fix branding to use `team_id` not `user_id`
- [ ] Decide: Subdomain or Team Context approach
- [ ] Raise Enterprise tier to $299-$499
- [ ] Add seat limits to tiers

### Important (Week 1):
- [ ] Test with 2-3 team members
- [ ] Verify branding shows for all team members
- [ ] Document team setup for customers

### Nice to Have (Month 1):
- [ ] Implement subdomain routing
- [ ] Add usage tracking per team
- [ ] Build team management UI

---

**Bottom Line:**
- ❌ $199 for 20 users = LOW profit
- ✅ $299 for 10 users = GOOD profit
- ✅ $499 for unlimited + domain = BEST profit

Charge based on VALUE, not just user count.
