from flask import Flask, render_template, request, redirect, url_for, session
from flask_mysqldb import MySQL

app = Flask(__name__)
app.secret_key = "safeconnect123"

# MySQL Configuration
app.config['MYSQL_HOST'] = 'localhost'
app.config['MYSQL_USER'] = 'root'
app.config['MYSQL_PASSWORD'] = ''
app.config['MYSQL_DB'] = 'safeconnect'

mysql = MySQL(app)

# ---------------- HOME ----------------

@app.route('/')
def home():
    return render_template('auth.html')

# ---------------- ABOUT ----------------

@app.route('/about')
def about():
    return render_template('about.html')
#---------------- ANALYSIS ----------------
@app.route('/analysis', methods=['GET', 'POST'])
def analysis():

    if request.method == 'POST':

        username = request.form['username']
        account_age = int(request.form['account_age'])
        followers = int(request.form['followers'])
        following = int(request.form['following'])
        posts = int(request.form['posts'])
        verified = request.form['verified']
        profile_picture = request.form['profile_picture']

        # AI Risk Score
        risk_score = 0
        reasons = []

        if account_age < 30:
            risk_score += 25
            reasons.append("Newly created account")

        if followers < 20:
            risk_score += 15
            reasons.append("Very few followers")

        if posts < 5:
            risk_score += 15
            reasons.append("Very few posts")

        if following > followers * 5:
            risk_score += 25
            reasons.append("Following/Follower ratio is suspicious")

        if verified == "No":
            risk_score += 10
            reasons.append("Account is not verified")

        if profile_picture == "No":
            risk_score += 10
            reasons.append("No profile picture")

        # Risk Level
        if risk_score <= 25:
            risk_level = "Safe"
        elif risk_score <= 60:
            risk_level = "Suspicious"
        else:
            risk_level = "High Risk"

            notify_cur = mysql.connection.cursor()
            notify_cur.execute(
                "INSERT INTO notifications(message) VALUES(%s)",
                (f"High Risk Account Detected: {username}",)
            )
            mysql.connection.commit()
            notify_cur.close()

        # Recommendation
        if risk_level == "Safe":
            recommendation = "This account appears trustworthy."

        elif risk_level == "Suspicious":
            recommendation = "Verify the account before interacting."

        else:
            recommendation = "Avoid sharing personal information."

        # Save to database
        cur = mysql.connection.cursor()

        cur.execute("""
            INSERT INTO profile_analysis
            (username, risk_score, risk_level)
            VALUES (%s, %s, %s)
        """, (username, risk_score, risk_level))

        mysql.connection.commit()
        cur.close()

        return render_template(
            'account_analysis.html',
            username=username,
            risk_score=risk_score,
            risk_level=risk_level,
            recommendation=recommendation,
            reasons=reasons
        )

    return render_template('account_analysis.html')
# ---------------- DASHBOARD ----------------
@app.route('/dashboard')
def dashboard():

    if 'user' not in session:
        return redirect(url_for('home'))

    cur = mysql.connection.cursor()

    # Dashboard Cards
    cur.execute("SELECT COUNT(*) FROM profile_analysis")
    total_analysis = cur.fetchone()[0]

    cur.execute("SELECT COUNT(*) FROM fake_accounts")
    fake_accounts = cur.fetchone()[0]

    cur.execute("SELECT COUNT(*) FROM friend_checks")
    friend_checks = cur.fetchone()[0]

    # Risk Analysis Statistics
    cur.execute("SELECT COUNT(*) FROM profile_analysis WHERE risk_level='Safe'")
    safe_count = cur.fetchone()[0]

    cur.execute("SELECT COUNT(*) FROM profile_analysis WHERE risk_level='Suspicious'")
    suspicious_count = cur.fetchone()[0]

    cur.execute("SELECT COUNT(*) FROM profile_analysis WHERE risk_level='High Risk'")
    highrisk_count = cur.fetchone()[0]

    # Friend Request Statistics
    cur.execute("""
        SELECT COUNT(*)
        FROM friend_checks
        WHERE recommendation='Safe to Accept'
    """)
    safe_friend = cur.fetchone()[0]

    cur.execute("""
        SELECT COUNT(*)
        FROM friend_checks
        WHERE recommendation='Proceed with Caution'
    """)
    caution_friend = cur.fetchone()[0]

    cur.execute("""
        SELECT COUNT(*)
        FROM friend_checks
        WHERE recommendation='Avoid Request'
    """)
    avoid_friend = cur.fetchone()[0]

    # Notifications
    try:
        cur.execute("""
            SELECT message
            FROM notifications
            ORDER BY id DESC
            LIMIT 5
        """)
        notifications = cur.fetchall()
    except:
        notifications = []

    cur.close()

    return render_template(
        'dashboard.html',
        total_analysis=total_analysis,
        fake_accounts=fake_accounts,
        friend_checks=friend_checks,
        safe_count=safe_count,
        suspicious_count=suspicious_count,
        highrisk_count=highrisk_count,
        safe_friend=safe_friend,
        caution_friend=caution_friend,
        avoid_friend=avoid_friend,
        notifications=notifications
    )
# ---------------- FAKE ACCOUNT DETECTION ----------------
@app.route('/fake-detection', methods=['GET', 'POST'])
def fake_detection():

    if request.method == 'POST':

        username = request.form['username']
        followers = int(request.form['followers'])
        following = int(request.form['following'])
        posts = int(request.form['posts'])
        profile_picture = request.form['profile_picture']
        bio = request.form['bio']

        probability = 0
        reasons = []

        if followers < 20:
            probability += 20
            reasons.append("Very few followers")

        if following > followers * 5:
            probability += 25
            reasons.append("Following/Follower ratio is suspicious")

        if posts < 5:
            probability += 20
            reasons.append("Very few posts")

        if profile_picture == "no":
            probability += 20
            reasons.append("No profile picture")

        if bio == "no":
            probability += 15
            reasons.append("No bio available")

        # Determine Result
        if probability >= 80:
            result = "Highly Fake"
            recommendation = "🚫 Avoid interacting with this account. It shows strong indicators of being fake."

        elif probability >= 50:
            result = "Possibly Fake"
            recommendation = "⚠ Verify this account before accepting requests or sharing personal information."

        else:
            result = "Likely Genuine"
            recommendation = "✅ No major fake account indicators were detected."

        # Add Notification
        if probability >= 50:

            notify_cur = mysql.connection.cursor()

            notify_cur.execute(
                "INSERT INTO notifications(message) VALUES(%s)",
                (f"Fake Account Detected: {username} ({result})",)
            )

            mysql.connection.commit()
            notify_cur.close()

        # Save Result
        cur = mysql.connection.cursor()

        cur.execute("""
            INSERT INTO fake_accounts
            (probability, result)
            VALUES (%s, %s)
        """, (probability, result))

        mysql.connection.commit()
        cur.close()

        return render_template(
            "fake_detection.html",
            username=username,
            probability=probability,
            result=result,
            recommendation=recommendation,
            reasons=reasons
        )

    return render_template("fake_detection.html")
# ---------------- FRIEND CHECKER ----------------
@app.route('/friend-checker', methods=['GET', 'POST'])
def friend_checker():

    if request.method == 'POST':

        username = request.form['username']
        account_age = int(request.form['account_age'])
        followers = int(request.form['followers'])
        following = int(request.form['following'])
        posts = int(request.form['posts'])
        verified = request.form['verified']
        profile_picture = request.form['profile_picture']

        trust_score = 100
        reasons = []

        if account_age < 30:
            trust_score -= 20
            reasons.append("New account (less than 30 days old)")

        if followers < 20:
            trust_score -= 15
            reasons.append("Very few followers")

        if posts < 5:
            trust_score -= 15
            reasons.append("Very few posts")

        if following > followers * 5:
            trust_score -= 30
            reasons.append("Following too many accounts compared to followers")

        if verified == "No":
            trust_score -= 10
            reasons.append("Account is not verified")

        if profile_picture == "No":
            trust_score -= 10
            reasons.append("No profile picture")

        # Prevent negative score
        if trust_score < 0:
            trust_score = 0

        if trust_score >= 80:
            recommendation = "Safe to Accept"

        elif trust_score >= 50:
            recommendation = "Proceed with Caution"

        else:
            recommendation = "Avoid Request"

        cur = mysql.connection.cursor()

        cur.execute("""
            INSERT INTO friend_checks
            (username, trust_score, recommendation)
            VALUES (%s, %s, %s)
        """, (username, trust_score, recommendation))

        mysql.connection.commit()
        cur.close()

        return render_template(
            'friend_checker.html',
            username=username,
            trust_score=trust_score,
            recommendation=recommendation,
            reasons=reasons
        )

    return render_template('friend_checker.html')
# ---------------- SCAM ANALYZER ----------------
@app.route('/scam-analyzer', methods=['GET','POST'])
def scam_analyzer():

    if request.method == 'POST':

        message = request.form['message'].lower()

        probability = 0

        keywords = []

        scam_type = "Safe"

        recommendation = "No scam detected."

        scam_words = {

            "won":20,
            "prize":20,
            "click":15,
            "otp":20,
            "bank":15,
            "urgent":10,
            "gift":15,
            "lottery":25,
            "verify":15,
            "password":25,
            "upi":20,
            "payment":20,
            "reward":20,
            "offer":15,
            "limited":10,
            "free":15

        }

        for word, score in scam_words.items():

            if word in message:

                probability += score

                keywords.append(word)

        probability = min(probability,100)

        if probability >= 80:

            scam_type = "Prize / Phishing Scam"

            recommendation = "Highly suspicious. Do NOT click links or share OTP/password."

        elif probability >= 50:

            scam_type = "Suspicious Message"

            recommendation = "Verify the sender before responding."

        else:

            scam_type = "Likely Safe"

            recommendation = "No major scam indicators found."

        cur = mysql.connection.cursor()

        cur.execute(
            """
            INSERT INTO scam_analysis(message,probability,scam_type)
            VALUES(%s,%s,%s)
            """,
            (message,probability,scam_type)
        )

        mysql.connection.commit()

        cur.close()

        return render_template(
            "scam_analyzer.html",
            scam_probability=probability,
            scam_type=scam_type,
            keywords=keywords,
            recommendation=recommendation
        )

    return render_template("scam_analyzer.html")

# ---------------- CONTACT ----------------

@app.route('/contact')
def contact():
    return render_template('contact.html')

# ---------------- REGISTER ----------------

@app.route('/register', methods=['GET', 'POST'])
def register():

    if request.method == 'POST':

        name = request.form['name']
        email = request.form['email']
        password = request.form['password']

        cur = mysql.connection.cursor()

        cur.execute(
            "INSERT INTO users(name, email, password) VALUES(%s, %s, %s)",
            (name, email, password)
        )

        mysql.connection.commit()
        cur.close()

        return redirect(url_for('login'))

    return render_template('register.html')

# ---------------- LOGIN ----------------

@app.route('/login', methods=['GET', 'POST'])
def login():

    if request.method == 'POST':

        email = request.form['email']
        password = request.form['password']

        cur = mysql.connection.cursor()

        cur.execute(
            "SELECT * FROM users WHERE email=%s AND password=%s",
            (email, password)
        )

        user = cur.fetchone()

        cur.close()

        if user:
            session['user'] = email
            return redirect(url_for('dashboard'))

        return "Invalid Email or Password"

    return render_template('login.html')

# ---------------- LOGOUT ----------------

@app.route('/logout')
def logout():

    session.pop('user', None)

    return redirect(url_for('home'))

# ---------------- TEST DATABASE ----------------

@app.route('/test-db')
def test_db():

    cur = mysql.connection.cursor()

    cur.execute("SELECT DATABASE();")

    data = cur.fetchone()

    cur.close()

    return f"Connected to database: {data[0]}"

# ---------------- RUN APP ----------------

if __name__ == '__main__':
    app.run(debug=True)