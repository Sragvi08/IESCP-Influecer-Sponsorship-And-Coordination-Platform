# InfluenceSync - Influencer Engagement and Sponsor Coordination Platform

**InfluenceSync** is a web-based platform designed to connect sponsors and influencers for seamless collaboration on marketing campaigns. The platform provides easy management of campaigns, ad requests, negotiations, and performance tracking, helping both sponsors and influencers streamline their influencer marketing efforts.

## Table of Contents
- [Features](#features)
- [Tech Stack](#tech-stack)
- [Installation](#installation)
- [Usage](#usage)
- [Database Models](#database-models)
- [License](#license)

## Features

- **Sponsor Campaign Management**: Sponsors can create, manage, and track campaigns.
- **Influencer Ad Requests**: Influencers can apply to campaigns that match their niche and audience reach.
- **Negotiation System**: Influencers can negotiate payment terms with sponsors, who can accept or reject the requests.
- **Profile Management**: Influencers and sponsors can manage their profiles with relevant details like niche, reach, budget, etc.
- **Search & Filter**: Influencers can search for active campaigns by niche and budget.
- **Dashboards**: Dedicated dashboards for Admins, Sponsors, and Influencers.
- **Admin Features**: Admins can manage all users and campaigns, and monitor the overall platform activity.

## Tech Stack

- **Backend**: Flask (Python)
- **Frontend**: Jinja2 templating, HTML, CSS (Bootstrap)
- **Database**: SQLite (via SQLAlchemy ORM)
- **Forms & Validation**: Flask-WTF
- **Templating**: Jinja2
- **Deployment**: (Optional) Deployed using Flask on local servers or any cloud platform.

## Installation

To run this project locally, follow these steps:

1. **Clone the repository**:

    ```bash
    git clone https://github.com/your-username/influence-sync.git
    cd influence-sync
    ```

2. **Create a virtual environment**:

    ```bash
    python3 -m venv venv
    source venv/bin/activate  # On Windows: venv\Scripts\activate
    ```

3. **Install dependencies**:

    ```bash
    pip install -r requirements.txt
    ```

4. **Set up the database**:

    Initialize your SQLite database:

    ```bash
    flask db init
    flask db migrate -m "Initial migration."
    flask db upgrade
    ```

5. **Run the application**:

    ```bash
    flask run
    ```

6. **Access the app**:
   - Open your web browser and go to `http://127.0.0.1:5000/`.

## Usage

- **Admin Role**:
  - Access the admin dashboard to manage users (sponsors, influencers), campaigns, and monitor overall activity.
  
- **Sponsor Role**:
  - Create campaigns, receive ad requests from influencers, track campaign progress, and handle negotiations.
  
- **Influencer Role**:
  - Browse and apply for campaigns, negotiate payment terms, and manage your profile (niche, reach, platform).

## Database Models

### User
- `id`: Primary key
- `name`: User's full name
- `role`: `admin`, `sponsor`, or `influencer`
- `email`: Email address
- `password_hash`: Password hash for authentication

### Campaign
- `id`: Primary key
- `sponsor_id`: ForeignKey to the sponsor creating the campaign
- `name`: Name of the campaign
- `niche`: Campaign niche
- `budget`: Total campaign budget
- `status`: Campaign status (active, ongoing, completed)

### AdRequest
- `id`: Primary key
- `campaign_id`: ForeignKey to the campaign
- `influencer_id`: ForeignKey to the influencer
- `message`: Ad request message
- `status`: Status (pending, accepted, rejected)

### Negotiation
- `id`: Primary key
- `ad_request_id`: ForeignKey to the ad request
- `new_payment_amount`: Negotiated payment amount
- `message`: Message from the influencer regarding the negotiation
- `status`: Status (pending, accepted, rejected)

## ER Diagram
![image](https://github.com/user-attachments/assets/3ba9f6c0-8319-4720-9486-86d1965a4d6d)


## License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.


