from flask import Flask, render_template, request, redirect, url_for, flash, session
from flask_sqlalchemy import SQLAlchemy
from datetime import datetime

app = Flask(__name__)


app.config['SECRET_KEY'] = "dev-secret-key"  
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///phg.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False


app.config['ADMIN_PASSWORD'] = "Evan"

db = SQLAlchemy(app)



class Event(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(120), nullable=False)
    category = db.Column(db.String(80))
    date = db.Column(db.String(50))
    location = db.Column(db.String(120))
    description = db.Column(db.Text)


class Registration(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    competitor_name = db.Column(db.String(120), nullable=False)
    email = db.Column(db.String(120), nullable=False)
    event_id = db.Column(db.Integer, db.ForeignKey('event.id'), nullable=False)
    team_name = db.Column(db.String(120))
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

    event = db.relationship('Event', backref=db.backref('registrations', lazy=True))



def init_db():
    with app.app_context():

        db.drop_all()
        db.create_all()

       
        e1 = Event(
            name="Football Tournament",
            category="Sports",
            date="2025-08-09",
            location="Paisley Sports Ground",
            description=(
                "A friendly football tournament for local teams and mixed groups. "
                "Matches are played in a five- or seven-a-side format, with short games "
                "scheduled throughout the day. Teams are drawn into a simple knock-out path, "
                "so every match feels meaningful and easy to follow. Basic kit and suitable "
                "footwear are required, but the focus is on fair play and community spirit "
                "rather than professional competition."
            )
        )

  
        e2 = Event(
            name="Hillwalking Challenge",
            category="Outdoor",
            date="2025-08-10",
            location="Gleniffer Braes Country Park",
            description=(
                "A guided hillwalking route around the hills above Paisley, offering wide views "
                "over the town and the Clyde valley. The route follows marked paths with a mix "
                "of gentle slopes and a few steeper sections, making it suitable for most fitness "
                "levels with sensible footwear. Marshals and checkpoints along the way help to keep "
                "groups on track and ensure that everyone completes the challenge safely. Waterproof "
                "clothing is recommended, and participants should carry water and a small snack."
            )
        )

        
        e3 = Event(
            name="Highland Dance Showcase",
            category="Cultural",
            date="2025-08-11",
            location="Main Stage",
            description=(
                "An evening programme of traditional Highland dancing, featuring both solo and group "
                "performances. Dancers present classic steps such as the Highland Fling and Sword Dance, "
                "accompanied by live pipe and drum music. The showcase is open to local dance schools and "
                "community groups, with separate time slots for younger performers and more experienced "
                "competitors. Seating is available around the main stage so that families and visitors can "
                "enjoy the atmosphere throughout the event."
            )
        )

        
        e4 = Event(
            name="Family Fun Run",
            category="Community",
            date="2025-08-11",
            location="Riverside Loop",
            description=(
                "A relaxed fun run designed for families and mixed age groups, following a short marked "
                "route along the riverside. The emphasis is on taking part and enjoying the day rather "
                "than chasing finishing times, and walkers are just as welcome as runners. Pushchairs and "
                "younger children can join as long as they are accompanied by an adult, and light fancy dress "
                "is encouraged for anyone who would like to add to the festival atmosphere. A simple check-in "
                "point at the start and finish helps organisers keep track of participants."
            )
        )

        db.session.add_all([e1, e2, e3, e4])
        db.session.commit()
        print("Database reset, 4 events inserted.")



@app.route("/")
def home():
    
    category = request.args.get("category")
    query = Event.query

    if category:
        query = query.filter_by(category=category)

    events = query.all()

   
    raw_categories = db.session.query(Event.category).distinct().all()
    categories = [c[0] for c in raw_categories if c[0]]

    return render_template(
        "home.html",
        events=events,
        categories=categories,
        selected_category=category
    )


@app.route("/events/<int:event_id>")
def event_detail(event_id):
    event = Event.query.get_or_404(event_id)
    return render_template("event_detail.html", event=event)


@app.route("/events/<int:event_id>/register", methods=["GET", "POST"])
def register(event_id):
    event = Event.query.get_or_404(event_id)

    if request.method == "POST":
        name = (request.form.get("name") or "").strip()
        email = (request.form.get("email") or "").strip()
        team = (request.form.get("team") or "").strip()

        if not name or not email:
            flash("Name and email are required.")
            return redirect(url_for("register", event_id=event_id))

        reg = Registration(
            competitor_name=name,
            email=email,
            team_name=team,
            event_id=event.id
        )
        db.session.add(reg)
        db.session.commit()
        flash("Registration submitted successfully!")
        return redirect(url_for("home"))

    return render_template("register.html", event=event)



@app.route("/admin/login", methods=["GET", "POST"])
def admin_login():
    if request.method == "POST":
        password = request.form.get("password", "")
        if password == app.config['ADMIN_PASSWORD']:
            session['admin_logged_in'] = True
            flash("Admin login successful.")
            next_url = request.args.get("next")
            return redirect(next_url or url_for("admin_registrations"))
        else:
            flash("Incorrect password.")
            return redirect(url_for("admin_login"))

    return render_template("admin_login.html")


@app.route("/admin/logout")
def admin_logout():
    session.pop('admin_logged_in', None)
    flash("You have been logged out.")
    return redirect(url_for("home"))


@app.route("/admin/registrations")
def admin_registrations():
   
    if not session.get('admin_logged_in'):
        flash("Please log in as admin to view registrations.")
        return redirect(url_for("admin_login", next=url_for("admin_registrations")))

    
    event_id = request.args.get("event_id", type=int)

    
    events = Event.query.order_by(Event.date).all()

    query = Registration.query.order_by(Registration.created_at.desc())
    if event_id:
        query = query.filter_by(event_id=event_id)

    regs = query.all()

    return render_template(
        "admin_registrations.html",
        regs=regs,
        events=events,
        selected_event_id=event_id
    )


if __name__ == "__main__":
    init_db()         
    app.run(debug=True)