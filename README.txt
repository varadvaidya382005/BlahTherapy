

# BlahTherapy  – Anonymous Mental Health Support Platform 💬🧠

This project is a web-based anonymous mental health support platform, built using **Flask**, **Firebase**, and **JavaScript**.

It allows users to talk anonymously, submit testimonials, post blogs, and interact with an emotionally aware interface that uses **sentiment analysis** to moderate the quality of submissions.

---

## 🛠 Tech Stack

- **Backend:** Flask (Python)
- **Frontend:** HTML, CSS, JS (Jinja templating)
- **Authentication:** Firebase Auth (Email & Google Login)
- **Database:** Firebase Firestore
- **Sentiment Analysis:** TextBlob (Python NLP)
- **Deployment:** Vercel (for frontend) / Render / Local (for backend)

---

## 🎯 Features

- 🧑‍💻 **User Authentication**
  - Sign up / Login with username & password (hashed with Werkzeug)
  - Google Sign-In via Firebase

- 📝 **Blogs**
  - Users can submit their own mental health-related blogs
  - Blogs are time-stamped and stored in Firestore
  - View and delete personal blogs

- 💬 **Testimonials**
  - Submit anonymous testimonials
  - Filtered using **TextBlob** sentiment analysis (only neutral or positive allowed)
  - Displayed randomly on homepage

- 🏠 **Homepage**
  - Shows rotating positive testimonials
  - Random blog entries to encourage engagement

- 🔒 **Session Management**
  - Flask session-based user login
  - Secure handling of passwords using hashing

- 🌍 **Timezone Support**
  - Timestamps recorded in IST using `pytz`

---

## 🧩 Folder Structure

blahtherapy-clone/
├── static/
│   └── firebase-adminsdk.json
├── templates/
│   ├── index.html
│   ├── 01_login_page.html
│   ├── 01_signup.html
│   ├── 02_blogs.html
│   ├── 03_blogs.html
│   ├── submit_testimonial.html
│   ├── testimonials.html
│   └── about_us.html
├── app.py
├── requirements.txt
└── README.md

---

## 🚀 Getting Started

### 1. Clone the repo

```bash
git clone https://github.com/your-username/blahtherapy-clone.git
cd blahtherapy-clone

2. Install dependencies

pip install -r requirements.txt

3. Add Firebase Admin SDK
	•	Download your Firebase service account key JSON
	•	Save it in the static/ folder and update the path in app.py if needed

4. Run the server

python app.py

Visit http://localhost:8000

⸻

🔐 Authentication Notes
	•	Google Sign-In sends a Firebase ID token via Authorization header
	•	Backend verifies this token and establishes session

⸻

📦 requirements.txt

Flask
firebase-admin
textblob
pytz
Werkzeug


⸻

📌 Routes Overview

Endpoint	Method	Description
/	GET	Homepage with blogs + testimonials
/login	GET/POST	Login with username/password
/signup	GET/POST	Create new user
/google_login	POST	Google login using Firebase token
/submit_blog	GET/POST	Submit new blog
/view_blogs	GET	View user’s submitted blogs
/delete_blog	POST	Delete a specific blog
/submit_testimonial	GET/POST	Add a testimonial (with sentiment check)
/testimonials	GET	View all testimonials
/about_us	GET	Static About Us page
/logout	GET	Logout and clear session


⸻

🧠 Sentiment Filtering Logic
	•	Uses TextBlob to evaluate sentiment polarity
	•	Only testimonials with neutral or positive polarity are stored
	•	Prevents submission of negative content to ensure a safe space

⸻

📌 Future Improvements
	•	Real-time chat feature (user ↔ listener or bot)
	•	Integrate GPT/Gemini API for AI therapist responses
	•	Crisis language detection with NLP
	•	Push to Firebase Hosting or Cloud Run
	•	Mobile responsive UI

⸻

📃 License

This project is licensed under the MIT License.

⸻

❤️ Built With Focus On
	•	Anonymous support
	•	User expression and emotional safety
	•	Pure logic — no AI models used for auto-replies yet
	•	Firebase + Flask + Vanilla JS for core features

⸻


Let me know if you'd also like a version with AI chat integration (e.g. Gemini or OpenAI), or want this split into separate Markdown sections for a docs site.
