from flask import render_template,redirect, url_for, request, flash, session
from app import app
from app import login_manager
from models import db, User, Influencer, Sponsor, Campaign, AdRequest, CampaignRequest
from werkzeug.security import generate_password_hash, check_password_hash
from flask_login import LoginManager, login_user, login_required, logout_user, current_user
import uuid as uuid
from datetime import datetime
import os

# basically the controllers.py
@app.route('/')  # it's the base url = 127.0.0.1:5000
def home():
    return render_template('home.html')

@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))

@app.route('/login',methods=['GET','POST'])
def login():
    if request.method == 'POST':
        username = request.form.get('username')
        password = request.form.get('password')

        if not username or not password:
            flash('Please fill out all the fields')
            return redirect(url_for('login'))
        
        user = User.query.filter_by(username=username).first()

        if not user:
            flash('Username does not exist','danger')
            return redirect(url_for('login'))
        
        if user.flagged:
            flash('You have been flagged by the admin', 'danger')
            return redirect(url_for('login'))
        
        if not check_password_hash(user.password_hash, password):
            flash('Incorrect Password','danger')
            return redirect(url_for('login'))
        
        login_user(user)
        flash('Login successful!', 'success')
        
        if user.role =='admin':
            return redirect(url_for('admin_dash'))
        elif user.role == 'sponsor':
            return redirect(url_for('sponsor_dash'))
        elif user.role == 'influencer':
            return redirect(url_for('influencer_dash'))
        else:
            flash('Unknown user role', 'danger')
            return redirect(url_for('login'))

    return render_template('login.html')

@app.route('/signup')
def signup():
    return redirect(url_for('home'))

@app.route('/sponser_reg', methods=['GET','POST'])
def sponsor_reg():
    if request.method == 'POST':
        username = request.form.get('username')
        email = request.form.get('email')
        password = request.form.get('password')
        confirm_password = request.form.get('confirm_password')
        company_name = request.form.get('company_name')
        industry = request.form.get('industry')

        if not username or not password or not confirm_password:
            flash('Please fill out required fields','danger')
            return redirect(url_for('sposnor_reg'))

        if password != confirm_password:
                flash('Passwords do not match!', 'danger')
                return redirect(url_for('sponsor_reg'))

        user = User.query.filter_by(username=username).first()

        # password hashing (for security)
        password_hash=generate_password_hash(password)

        if user:
            flash('Uh oh! Looks like the username already exists.','danger')
            return redirect(url_for('sposnor_reg'))
        new_user = User(username=username, email=email, password_hash=password_hash, role='sponsor')
        db.session.add(new_user)
        db.session.commit()

        new_sponsor = Sponsor(
            user_id=new_user.id,
            company_name=company_name,
            industry=industry,
        )
        db.session.add(new_sponsor)
        db.session.commit()

        flash('Sponsor registration successful!', 'success')
        return redirect(url_for('login'))

    return render_template('sponsor_reg.html')

# def allowed_file(filename):
#     return '.' in filename and filename.rsplit('.',1)[1].lower() in app.config['ALLOWED_EXTENSIONS']

@app.route('/influencer_registration',methods=['GET', 'POST'])
def influencer_reg():
    if request.method == 'POST':
        username = request.form.get('username')
        email = request.form.get('email')
        password = request.form.get('password')
        confirm_password = request.form.get('confirm_password')
        niche = request.form.get('niche')
        reach = request.form.get('reach')
        platform = request.form.get('platform')
        
    
        if not username or not password or not confirm_password:
            flash('Please fill out required fields','danger')
            return redirect(url_for('influencer_reg'))

        if password != confirm_password:
                flash('Passwords do not match!', 'danger')
                return redirect(url_for('influencer_reg'))

        user = User.query.filter_by(username=username).first()

        # password hashing (for security)
        password_hash=generate_password_hash(password)

        if user:
            flash('Uh oh! Looks like the username already exists.','danger')
            return redirect(url_for('influencer_reg'))
        new_user = User(username=username, email=email, password_hash=password_hash, role='influencer')
        db.session.add(new_user)
        db.session.commit()


        new_influencer = Influencer(
            user_id=new_user.id,
            niche=niche,
            reach=reach,
            platform=platform
        )
        db.session.add(new_influencer)
        db.session.commit()

        flash('Influencer registration successful!', 'success')
        return redirect(url_for('login'))
    
    return render_template('influencer_reg.html')

@app.route('/influencer_dash')
@login_required
def influencer_dash():
    user = current_user
    if user.role == 'influencer':
        influencer = Influencer.query.filter_by(user_id=user.id).first()
        
        active_campaigns = AdRequest.query.filter(
            AdRequest.influencer_id == influencer.id,
            AdRequest.status == 'accepted'
        ).all()
        

        new_requests = AdRequest.query.filter(
            AdRequest.influencer_id == influencer.id,
            AdRequest.status == 'pending'
        ).all()

        campaigns_with_progress = []
        for ad_request in active_campaigns:
            campaign = ad_request.campaign
            progress = campaign.progress
            campaigns_with_progress.append({
                'campaign': campaign,
                'progress': progress
            })

        completed_requests = AdRequest.query.filter_by(
            influencer_id=influencer.id, status='done').all()
        
        rejected_campaign_requests = CampaignRequest.query.filter(
            CampaignRequest.influencer_id == influencer.id,
            CampaignRequest.status == 'rejected'
        ).all()
        
        return render_template('influencer_dash.html', 
                               user=user, influencer=influencer, 
                               active_campaigns=campaigns_with_progress,
                               new_requests=new_requests, 
                               completed_requests=completed_requests,
                               rejected_campaign_requests=rejected_campaign_requests)
    else:
        flash('Unauthorized access!', 'danger')
        return redirect(url_for('login'))


#### Influencer dash new request routes

@app.route('/view_ad_request/<int:request_id>', methods=['GET'])
@login_required
def view_ad_request(request_id):
    ad_request = AdRequest.query.get_or_404(request_id)
    return render_template('view_ad_request.html', ad_request=ad_request)

@app.route('/accept_ad_request/<int:request_id>', methods=['POST'])
@login_required
def accept_ad_request(request_id):
    ad_request = AdRequest.query.get_or_404(request_id)

    ad_request.status = 'accepted'
    campaign = ad_request.campaign
    campaign.status = 'ongoing'
    
    try:
        db.session.commit()
        flash('Ad request accepted successfully!', 'success')
    except:
        db.session.rollback()
        flash('There was an issue accepting the ad request.', 'danger')

    return redirect(url_for('influencer_dash'))

@app.route('/reject_ad_request/<int:request_id>', methods=['POST'])
@login_required
def reject_ad_request(request_id):
    ad_request = AdRequest.query.get_or_404(request_id)
    ad_request.status = 'rejected'
    db.session.commit()
    
    try:
        db.session.commit()
        flash('Ad request rejected successfully!', 'success')
    except:
        db.session.rollback()
        flash('There was an issue rejecting the ad request.', 'danger')

    return redirect(url_for('influencer_dash'))
    
##### Search campaigns tab 

@app.route('/search_campaigns', methods=['GET', 'POST'])
@login_required
def search_campaigns():
    user =current_user
    if user.role != 'influencer':
        flash('Unauthorized access!', 'danger')
        return redirect(url_for('login'))
    

    niche_filter = request.form.get('niche', '').strip()
    min_budget_filter = request.form.get('min_budget', type=float)
    
    query = Campaign.query.filter(
        Campaign.visibility == 'public',
        Campaign.status == 'active'
    )

    if niche_filter:
        query = query.filter(Campaign.niche.ilike(f'%{niche_filter}%'))
    if min_budget_filter is not None:  
        query = query.filter(Campaign.budget >= min_budget_filter)

    campaigns = query.all()
    
    return render_template('influencer_search_camp.html', user=user, campaigns=campaigns)

##### Campaign Request part 
@app.route('/create_campaign_request/<int:campaign_id>/<int:influencer_id>', methods=['POST'])
@login_required
def create_campaign_request(campaign_id, influencer_id):
    message = request.form.get('message')

    # Create a new CampaignRequest
    new_request = CampaignRequest(
        campaign_id=campaign_id,
        influencer_id=influencer_id,
        message=message,
        status='Pending'
    )

    # Add the new request to the database
    try:
        db.session.add(new_request)
        db.session.commit()
        flash('Your request has been sent successfully!', 'success')
    except Exception as e:
        db.session.rollback()
        flash(f'An error occurred: {str(e)}. Please try again.', 'danger')

    return redirect(url_for('search_campaigns'))

#### Sponsor page -------------------------------

@app.route('/sponsor_dash')
@login_required
def sponsor_dash():
    user = current_user
    if user.role == 'sponsor':
        sponsor = Sponsor.query.filter_by(user_id=user.id).first()
        # Fetch campaigns with status 'active' or 'ongoing'
        campaigns = Campaign.query.filter(
            Campaign.sponsor_id == sponsor.id,
            Campaign.status.in_(['active', 'ongoing'])
        ).all()  
        
        new_requests = CampaignRequest.query.join(Campaign).filter(
            CampaignRequest.campaign_id == Campaign.id,
            Campaign.sponsor_id == sponsor.id,
            CampaignRequest.status == 'Pending'
        ).all()

        return render_template('sponsor_dash.html', user=user, campaigns=campaigns, new_requests=new_requests)
    else:
        flash('Unauthorized access!', 'danger')
        return redirect(url_for('login'))
    
## all the sponsor details ----------
    
@app.route('/sponsor_campaigns')
@login_required
def sponsor_campaigns():
    user=current_user
    if user.role == 'sponsor':
        sponsor = Sponsor.query.filter_by(user_id=user.id).first()
        niche = request.args.get('niche')
        visibility = request.args.get('visibility')

        campaigns_query = Campaign.query.filter_by(sponsor_id=sponsor.id)

        if niche:
            campaigns_query = campaigns_query.filter(Campaign.niche.ilike(f'%{niche}%'))
        if visibility:
            campaigns_query = campaigns_query.filter(Campaign.visibility.ilike(f'%{visibility.lower()}%'))

        campaigns = campaigns_query.all()
        
        return render_template('sponsor_campaigns.html', sponsor=sponsor, campaigns=campaigns)
    else:
        flash('Unauthorized access!', 'danger')
        return redirect(url_for('login'))



@app.route('/add_campaign', methods=['POST'])
@login_required
def add_campaign():
    user = current_user
    if user.role == 'sponsor':
        sponsor = Sponsor.query.filter_by(user_id=user.id).first()
        
        name = request.form.get('name')
        description = request.form.get('description')
        niche = request.form.get('niche')
        goals = request.form.get('goals')
        budget = float(request.form.get('budget'))
        visibility = request.form.get('visibility')
        start_date_str = request.form.get('start_date')
        end_date_str = request.form.get('end_date')

        start_date = datetime.strptime(start_date_str, '%Y-%m-%d').date() if start_date_str else None
        end_date = datetime.strptime(end_date_str, '%Y-%m-%d').date() if end_date_str else None

        
        new_campaign = Campaign(
            name=name,
            description=description,
            niche=niche,
            goals=goals,
            budget=budget,
            visibility=visibility,
            start_date=start_date,
            end_date=end_date,
            status='active',
            sponsor_id=sponsor.id
        )
        
        db.session.add(new_campaign)
        db.session.commit()
        
        flash('Campaign created successfully!', 'success')
        return redirect(url_for('sponsor_campaigns'))
    else:
        flash('Unauthorized access!', 'danger')
        return redirect(url_for('login'))
    
@app.route('/campaign/<int:campaign_id>')
@login_required
def campaign_details(campaign_id):
    user = current_user
    if user and user.role == 'sponsor':
        campaign = Campaign.query.get_or_404(campaign_id)

        ad_requests = AdRequest.query.filter(
            AdRequest.campaign_id == campaign_id,
            AdRequest.status.in_(['pending', 'rejected'])
        ).all()

        ongoing_ads = AdRequest.query.filter_by(campaign_id=campaign_id, status='accepted').all()
        completed_ads = AdRequest.query.filter_by(campaign_id=campaign_id, status='done').all()

        return render_template(
            'campaigns/campaign_details.html',
            campaign=campaign,
            ad_requests=ad_requests,
            ongoing_ads=ongoing_ads,
            completed_ads=completed_ads
        )
    else:
        flash('Unauthorized access!', 'danger')
        return redirect(url_for('login'))

@app.route('/edit_campaign/<int:campaign_id>',methods=['GET', 'POST'])
def edit_campaign(campaign_id):
    campaign = Campaign.query.get_or_404(campaign_id)
    if request.method == 'POST':
        campaign.name = request.form['name']
        campaign.description = request.form['description']
        campaign.start_date = datetime.strptime(request.form['start_date'], '%Y-%m-%d')
        campaign.end_date = datetime.strptime(request.form['end_date'], '%Y-%m-%d')
        campaign.budget = float(request.form['budget'])
        campaign.visibility = request.form['visibility']
        campaign.goals = request.form['goals']
        campaign.niche = request.form['niche']
        campaign.status = request.form['status']
        db.session.commit()
        flash('Campaign updated successfully!', 'success')
        return redirect(url_for('campaign_details', campaign_id=campaign.id))
    return render_template('campaigns/edit_campaign.html', campaign=campaign)

@app.route('/delete_campaign/<int:campaign_id>', methods=['POST'])
def delete_campaign(campaign_id):
    campaign = Campaign.query.get_or_404(campaign_id)
    db.session.delete(campaign)
    db.session.commit()
    flash('Campaign deleted successfully!', 'success')
    return redirect(url_for('sponsor_campaigns'))

### find influencer in sponsor

@app.route('/sponsor_find_inf', methods=['GET', 'POST'])
def sponsor_find_inf():
    name_filter = request.form.get('name', '')
    niche_filter = request.form.get('niche', '')
    min_reach_filter = request.form.get('min_reach', 0, type=int)
    
    query = Influencer.query.join(User)
    if name_filter:
        query = query.filter(User.username.ilike(f"%{name_filter}%"))
    if niche_filter:
        query = query.filter(Influencer.niche.ilike(f"%{niche_filter}%"))
    if min_reach_filter:
        query = query.filter(Influencer.reach >= min_reach_filter)
    
    influencers = query.all()
    campaigns = Campaign.query.all()
    
    return render_template('sponsor_find_inf.html', influencers=influencers, campaigns=campaigns)

### Ad requests-------------

@app.route('/send_ad_request_page/<int:influencer_id>', methods=['GET'])
def send_ad_request_page(influencer_id):
    influencer = Influencer.query.get_or_404(influencer_id)
    campaigns = Campaign.query.filter(
        (Campaign.status == 'active') | 
        ((Campaign.status == 'ongoing') & 
         (Campaign.ad_requests.any(AdRequest.influencer_id == influencer_id)))
    ).all()
    return render_template('ads/create_ad_req.html', influencer=influencer, campaigns=campaigns)  

@app.route('/send_ad_request', methods=['POST'])
def send_ad_request():
    influencer_id = request.form['influencer_id']
    campaign_id = request.form['campaign_id']
    requirements = request.form['requirements']
    message = request.form['message']
    payment_amount = request.form['payment_amount']
    
    new_ad_request = AdRequest(
        campaign_id=campaign_id,
        influencer_id=influencer_id,
        requirements=requirements,
        message=message,
        payment_amount=payment_amount,
        status='pending'
    )
    
    db.session.add(new_ad_request)
    db.session.commit()
    
    flash('Ad request sent successfully!', 'success')
    return redirect(url_for('sponsor_find_inf'))


### for completed ads marked as done 
@app.route('/mark_ad_done/<int:ad_request_id>', methods=['POST'])
def mark_ad_done(ad_request_id):
    ad_request = AdRequest.query.get_or_404(ad_request_id)
    if ad_request.status != 'done':
        ad_request.status = 'done'

        influencer = ad_request.influencer
        influencer.total_earnings += ad_request.payment_amount

        db.session.commit()
        
        flash('Ad marked as done, and influencer earnings updated.', 'success')
    else:
        flash('This ad is already marked as done.', 'warning')
    
    return redirect(url_for('campaign_details', campaign_id=ad_request.campaign_id))


@app.route('/edit_ad_request/<int:request_id>', methods=['GET', 'POST'])
def edit_ad_request(request_id):
    ad_request = AdRequest.query.get_or_404(request_id)
    if request.method == 'POST':
        ad_request.message = request.form['message']
        ad_request.requirements = request.form['requirements']
        ad_request.payment_amount = float(request.form['payment_amount'])
        ad_request.status = request.form['status']
        db.session.commit()
        flash('Ad request updated successfully!', 'success')
        return redirect(url_for('campaign_details', campaign_id=ad_request.campaign_id))
    return render_template('ads/edit_ad_request.html', ad_request=ad_request)

### delete add req -----------
@app.route('/delete_ad_request/<int:request_id>', methods=['POST'])
def delete_ad_request(request_id):
    ad_request = AdRequest.query.get_or_404(request_id)
    campaign_id = ad_request.campaign_id
    db.session.delete(ad_request)
    db.session.commit()
    flash('Ad request deleted successfully!', 'success')
    return redirect(url_for('campaign_details', campaign_id=campaign_id))


#### Handling new camp requests in sponsor dash
@app.route('/accept_camp_request/<int:request_id>', methods=['POST'])
def accept_camp_request(request_id):
    request_obj = CampaignRequest.query.get_or_404(request_id)

    requirements = request.form.get('requirements')
    payment_amount = request.form.get('payment_amount')

    ad_request = AdRequest(
        requirements=requirements,
        payment_amount=payment_amount,
        status='accepted',
        campaign_id=request_obj.campaign_id,
        influencer_id=request_obj.influencer_id,
        message=request_obj.message
    )
    db.session.add(ad_request)
    
    request_obj.status = 'accepted'
    campaign = Campaign.query.get(request_obj.campaign_id)
    campaign.status = 'ongoing'
    
    db.session.commit()
    
    flash('Request accepted and ad request created!', 'success')
    return redirect(url_for('sponsor_dash'))

@app.route('/reject_camp_request/<int:request_id>', methods=['POST'])
def reject_camp_request(request_id):
    request_obj = CampaignRequest.query.get_or_404(request_id)
    request_obj.status = 'rejected'
    db.session.commit()
    
    flash('Request rejected.', 'success')
    return redirect(url_for('sponsor_dash'))


@app.route('/admin_dash')
@login_required
def admin_dash():
    user = current_user
    if  user.role == 'admin':
        users = User.query.all()  # Fetch all users from the database
        total_users = User.query.count()
        total_influencers = Influencer.query.count()
        total_sponsors = Sponsor.query.count()
        total_campaigns = Campaign.query.count()
        total_ad_requests = AdRequest.query.count()

         # Data for bar chart
        total_ad_requests = AdRequest.query.count()
        categories_data = {
            'campaigns': total_campaigns,
            'ad_requests': total_ad_requests,
            'sponsors': total_sponsors,
            'influencers': total_influencers
        }

        flagged_influencers = User.query.filter_by(role='influencer', flagged=True).count()
        normal_influencers = total_influencers - flagged_influencers
        flagged_sponsors = User.query.filter_by(role='sponsor', flagged=True).count()
        normal_sponsors = total_sponsors - flagged_sponsors

        pie_chart_1_data = {
            'flagged_influencers': flagged_influencers,
            'normal_influencers': normal_influencers,
            'flagged_sponsors': flagged_sponsors,
            'normal_sponsors': normal_sponsors
        }

         # Data for second pie chart (Campaigns based on niche)
        niches = Campaign.query.with_entities(Campaign.niche, db.func.count(Campaign.id)).group_by(Campaign.niche).all()
        pie_chart_2_data = {niche: count for niche, count in niches}

        return render_template(
            'admin_dash.html',
            users=users,
            total_users=total_users,
            total_influencers=total_influencers,
            total_sponsors=total_sponsors,
            total_campaigns=total_campaigns,
            categories_data=categories_data,
            pie_chart_1_data=pie_chart_1_data,
            pie_chart_2_data=pie_chart_2_data
        )
    else:
        flash('Unauthorized access!', 'danger')
        return redirect(url_for('login'))


#### Other admin routes 
@app.route('/admin_sponsors')
@login_required
def admin_sponsors():
    user = current_user
    if user.role == 'admin':
        sponsors = Sponsor.query.all()  

        # Campaign status data
        campaign_status_data = {
            'active': Campaign.query.filter_by(status='active').count(),
            'ongoing': Campaign.query.filter_by(status='ongoing').count(),
            'completed': Campaign.query.filter_by(status='completed').count()
        }

        return render_template('admin_sponsor.html', sponsors=sponsors, campaign_status_data=campaign_status_data)
    else:
        flash('Unauthorized access!', 'danger')
        return redirect(url_for('login'))

@app.route('/toggle_flag_sponsor/<int:sponsor_id>', methods=['POST'])
def toggle_flag_sponsor(sponsor_id):
    sponsor = Sponsor.query.get_or_404(sponsor_id)
    sponsor.user.flagged = not sponsor.user.flagged  
    db.session.commit()
    if sponsor.user.flagged:
        flash(f'Sponsor {sponsor.company_name} has been flagged.', 'danger')
    else:
        flash(f'Sponsor {sponsor.company_name} has been unflagged.', 'success')
    return redirect(url_for('admin_sponsors'))

@app.route('/admin_influencers')
@login_required
def admin_influencers():
    user = current_user
    if user.role == 'admin':
        influencers = db.session.query(Influencer, User).join(User, Influencer.user_id == User.id).all()

        niches = {}
        platforms = {}
        
        for influencer, user in influencers:
            niches[influencer.niche] = niches.get(influencer.niche, 0) + 1
            platforms[influencer.platform] = platforms.get(influencer.platform, 0) + 1
        
        return render_template('admin_influencer.html', 
                               user=user,
                               influencers=influencers, 
                               niches=niches, 
                               platforms=platforms)
    else:
        flash('Unauthorized access!', 'danger')
        return redirect(url_for('login'))

@app.route('/toggle_flag_user/<int:user_id>', methods=['POST'])
def toggle_flag_user(user_id):
    user = User.query.get_or_404(user_id)
    user.flagged = not user.flagged
    db.session.commit()
    return redirect(url_for('admin_influencers'))


#### Profile page of sponsor
@app.route('/sponsor_profile', methods=['GET', 'POST'])
@login_required
def sponsor_profile():
    user = current_user
    if user.role == 'sponsor':
        sponsor = Sponsor.query.filter_by(user_id=user.id).first()
        if request.method == 'POST':
            sponsor.company_name = request.form['company_name']
            sponsor.industry = request.form['industry']
            db.session.commit()
            flash('Profile updated successfully!', 'success')
            return redirect(url_for('sponsor_profile'))
        return render_template('sponsor_profile.html', sponsor=sponsor)
    else:
        flash('Unauthorized access!', 'danger')
        return redirect(url_for('login'))

#### Profile page of Influencer
@app.route('/influencer_profile', methods=['GET', 'POST'])
@login_required
def influencer_profile():
    user = current_user
    if user.role == 'influencer':
        influencer = Influencer.query.filter_by(user_id=user.id).first()
        if request.method == 'POST':
            influencer.niche = request.form['niche']
            influencer.reach = request.form['reach']
            influencer.platform = request.form['platform']
            db.session.commit()
            flash('Profile updated successfully!', 'success')
            return redirect(url_for('influencer_profile'))
        return render_template('influencer_profile.html', influencer=influencer)
    else:
        flash('Unauthorized access!', 'danger')
        return redirect(url_for('login'))

@app.route('/logout')
@login_required
def logout():
    logout_user()
    flash('You have been logged out.', 'info')
    return redirect(url_for('login'))


