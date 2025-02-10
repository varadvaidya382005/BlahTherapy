from flask import Flask, render_template, request, redirect, url_for, flash, session, jsonify
import firebase_admin
from firebase_admin import credentials, firestore, auth
from werkzeug.security import generate_password_hash, check_password_hash
import os
from random import sample
import random
from datetime import datetime
import pytz  # For timezone support
from textblob import TextBlob  # For sentiment analysis

app = Flask(__name__)

# Set a secret key for sessions (ensure this is secure in production)
app.secret_key = os.environ.get('SECRET_KEY', 'fallback_secret_key')

# Firebase setup
service_account_path = os.path.join(app.root_path, 'static', 'blahtherapy-b5d52-firebase-adminsdk-keha7-a2d8e2f739.json')
cred = credentials.Certificate(service_account_path)
firebase_admin.initialize_app(cred)
db = firestore.client()

# Sentiment analysis function using TextBlob
def analyze_sentiment(text):
    blob = TextBlob(text)
    polarity = blob.sentiment.polarity  # Ranges from -1 (negative) to 1 (positive)
    if polarity > 0:
        return "good"  # Positive sentiment
    elif polarity < 0:
        return "bad"  # Negative sentiment
    else:
        return "neutral"  # Neutral sentiment

@app.route("/")
def home():
    # Check if user is logged in
    user_logged_in = session.get('username') is not None
    user_name = session.get('username', 'Not Logged In')

    # Fetch all blogs from Firestore
    blogs_ref = db.collection("blogs").stream()
    all_blogs = [{"id": blog.id, **blog.to_dict()} for blog in blogs_ref]

    # Select 8 random blogs
    random_blogs = sample(all_blogs, min(8, len(all_blogs)))

    # Fetch testimonials from Firestore
    testimonials_ref = db.collection("testimonials").stream()

    # Create a list of testimonials
    testimonials_list = [{"quote": t.to_dict()['quote'], "name": t.to_dict()['name'], "member_since": t.to_dict()['member_since']} for t in testimonials_ref]

    # Shuffle the testimonials list and take the first 3
    random.shuffle(testimonials_list)
    random_testimonials = testimonials_list[:3]

    return render_template('index.html', user_logged_in=user_logged_in, user_name=user_name, blogs=random_blogs, testimonials=random_testimonials)

@app.route("/login", methods=["GET", "POST"])
def login_page():
    if request.method == "POST":
        username = request.form['username']
        password = request.form['password']

        users_ref = db.collection('testing_users')
        query = users_ref.where('username', '==', username).limit(1)
        results = query.stream()

        user_exists = False
        for user in results:
            if check_password_hash(user.to_dict()['password'], password):
                user_exists = True
                break

        if user_exists:
            session['username'] = username  # Store username in session
            flash('Login successful!', 'success')
            return redirect(url_for('home'))
        else:
            flash('Invalid username or password. Please try again.', 'danger')
            return redirect(url_for('login_page'))

    return render_template("01_login_page.html")

@app.route("/logout")
def logout():
    session.pop('username', None)  # Clear the username from the session
    flash('You have been logged out.', 'success')
    return redirect(url_for('home'))  # Redirect to the homepage after logout

@app.route("/signup", methods=["GET", "POST"])
def signup_page():
    if request.method == "POST":
        username = request.form['username']
        password = request.form['password']

        users_ref = db.collection('testing_users')
        query = users_ref.where('username', '==', username).limit(1)
        results = query.stream()

        if any(results):
            flash('Username already exists. Please choose another username.', 'danger')
            return redirect(url_for('signup_page'))

        password_hash = generate_password_hash(password)  # Hash password
        users_ref.add({
            'username': username,
            'password': password_hash
        })

        flash('Account created successfully! Please login.', 'success')
        return redirect(url_for('login_page'))

    return render_template("01_signup.html")

@app.route("/google_login", methods=["POST"])
def google_login():
    # Check for Authorization header
    auth_header = request.headers.get("Authorization")
    if not auth_header:
        return jsonify({"error": "Authorization header missing"}), 400

    # Extract the ID token
    id_token = auth_header.split(" ").pop()
    if not id_token:
        return jsonify({"error": "ID token missing in Authorization header"}), 400

    try:
        # Verify the token using Firebase Admin SDK
        decoded_token = auth.verify_id_token(id_token)
        uid = decoded_token["uid"]

        # Fetch user info using the decoded UID
        user = auth.get_user(uid)
        session["username"] = user.display_name if user.display_name else "User"
        session["email"] = user.email

        flash("Google login successful!", "success")
        return jsonify({"success": True})

    except Exception as e:
        flash(f"Google login failed: {str(e)}", "danger")
        return jsonify({"error": f"Authentication failed: {str(e)}"}), 400

@app.route("/submit_blog", methods=["GET", "POST"])
def submit_blog():
    if "username" not in session:
        flash("You must log in to submit a blog.", "danger")
        return redirect(url_for("login_page"))

    if request.method == "POST":
        name = request.form["name"]
        year = request.form["year"]
        story = request.form["story"]

        # Validate inputs
        if not name or not year or not story:
            flash("All fields are required.", "danger")
            return redirect(url_for("submit_blog"))

        # Fetch current time in IST
        ist = pytz.timezone("Asia/Kolkata")
        current_time = datetime.now(ist)

        # Store blog in Firestore with user's username and current IST datetime
        blog_data = {
            "name": name,
            "year": year,
            "story": story,
            "author": session["username"],
            "time": current_time  # Add IST datetime
        }
        db.collection("blogs").add(blog_data)
        flash("Blog submitted successfully!", "success")
        return redirect(url_for("view_blogs"))

    return render_template("02_blogs.html")

@app.route("/view_blogs")
def view_blogs():
    if "username" not in session:
        flash("You must log in to view your blogs.", "danger")
        return redirect(url_for("login_page"))

    # Fetch blogs from Firestore for the logged-in user
    blogs_ref = db.collection("blogs").where("author", "==", session["username"]).stream()
    blogs = [{"id": blog.id, **blog.to_dict()} for blog in blogs_ref]

    return render_template("03_blogs.html", blogs=blogs)

@app.route("/delete_blog", methods=["POST"])
def delete_blog():
    if "username" not in session:
        flash("You must be logged in to perform this action.", "danger")
        return redirect(url_for("login_page"))

    blog_id = request.form.get("blog_id")
    if not blog_id:
        flash("Blog ID is missing.", "danger")
        return redirect(url_for("view_blogs"))

    try:
        db.collection("blogs").document(blog_id).delete()
        flash("Blog deleted successfully.", "success")
    except Exception as e:
        flash(f"An error occurred: {e}", "danger")

    return redirect(url_for("view_blogs"))
@app.route("/submit_testimonial", methods=["GET", "POST"])
def submit_testimonial():
    if "username" not in session:
        flash("You must log in to submit a testimonial.", "danger")
        return redirect(url_for("login_page"))

    if request.method == "POST":
        quote = request.form["quote"]
        member_since = request.form["member_since"]

        # Use the logged-in user's username
        name = session["username"]

        # Validate input fields
        if not quote or not name or not member_since:
            flash("All fields are required.", "danger")
            return redirect(url_for("submit_testimonial"))

        # Analyze the sentiment of the testimonial
        sentiment = analyze_sentiment(quote)

        # If sentiment is negative, don't submit the testimonial
        if sentiment == "bad":
            flash("Your testimonial contains negative sentiment. Please try again.", "danger")
            return redirect(url_for("submit_testimonial"))

        # Add the testimonial to Firestore if sentiment is good or neutral
        db.collection("testimonials").add({
            "quote": quote,
            "name": name,  # Use session username as the name
            "member_since": member_since
        })

        flash("Testimonial submitted successfully!", "success")
        return redirect(url_for("testimonials"))

    return render_template("submit_testimonial.html")
@app.route("/testimonials")
def testimonials():
    # Fetch testimonials from Firestore
    testimonials_ref = db.collection("testimonials").stream()
    testimonials_list = [{
        "quote": t.to_dict()['quote'],
        "name": t.to_dict()['name'],
        "member_since": t.to_dict()['member_since'],
        "sentiment": analyze_sentiment(t.to_dict()['quote'])  # Get sentiment
    } for t in testimonials_ref]

    return render_template("testimonials.html", testimonials=testimonials_list)

@app.route("/about_us")
def about_us():
    return render_template("about_us.html")

if __name__ == "__main__":
    app.run(debug=True, port=8000)