from app import app, db, Event


with app.app_context():
   
    db.create_all()

   
    existing = Event.query.all()
    if existing:
        print("Events already exist in the database:")
        for e in existing:
            print(e.id, e.name)
    else:
        e1 = Event(
            name="Caber Toss",
            category="Traditional",
            date="2025-08-10",
            location="Paisley Park",
            description="Competitors toss a large tapered pole called a caber as far as possible."
        )
        e2 = Event(
            name="Highland Dance",
            category="Cultural",
            date="2025-08-11",
            location="Main Stage",
            description="A showcase of traditional Scottish Highland dances accompanied by live music."
        )

        db.session.add_all([e1, e2])
        db.session.commit()

        print("Seed data inserted:")
        for e in Event.query.all():
            print(e.id, e.name)
