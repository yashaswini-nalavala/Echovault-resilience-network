# Echovault-resilience-network
A human-powered resilience network connecting people across time through shared survival stories and emotional impact tracking
🧩 1️⃣ PROBLEM STATEMENT

In today’s digital world, social platforms are overloaded with content, algorithms, and distractions. There is no lightweight platform focused purely on:

• Meaningful micro-interactions
• Simple connection building
• Direct appreciation sharing
• Gamified engagement through referrals and points

Most platforms are complex, ad-heavy, and attention-driven.

We identified the need for a:

Simple, lightweight, engagement-based social platform that encourages meaningful interaction rather than content overload.

🎯 2️⃣ PROPOSED SOLUTION

We developed Echo, a minimal social networking platform that enables users to:

• Connect with others
• Send and receive short appreciation messages called “Echoes”
• Follow users through request system
• Chat personally
• Earn points via engagement
• Track growth via leaderboard

Echo promotes positive engagement instead of content addiction.

💡 3️⃣ KEY FEATURES
👤 User System

Register / Login

Secure session management

Points reward system

🧑‍🤝‍🧑 Social Features

View other profiles

Follow request (Pending → Accept)

Followers / Following count

Notifications for requests

💬 Communication

Personal chat system

Timestamped messages

📣 Echo System

Send Echo (short appreciation message)

Receive Echo

Like Echo

Earn points per Echo sent

🏆 Gamification

Points leaderboard

Echo reward (+5 points)

🖼 Profile Customization

Bio editing

Profile picture upload

Default image handling

🔍 Search System

Search users by username

🏗 4️⃣ SYSTEM ARCHITECTURE

User → Flask Backend → SQLite Database
           ↓
   HTML Templates + CSS UI

Architecture Type:

Monolithic Web Application using MVC pattern.

🛠 5️⃣ TECH STACK
💻 Frontend

• HTML5
• CSS3
• Jinja2 (Flask Template Engine)

⚙ Backend

• Python 3
• Flask Framework

🗄 Database

• SQLite3

🔐 Security

• Session-based authentication
• Secure filename upload (Werkzeug)
• File type validation

📂 Storage

• Local file system (for profile images)

🗃 6️⃣ DATABASE DESIGN
users table

id (Primary Key)

username

password

bio

profile_pic

referral_code

points

follows table

id

follower_id

following_id

status (pending/accepted)

messages table

id

sender_id

receiver_id

message

time

echoes table

id

sender_id

receiver_id

content

likes

🔄 7️⃣ WORKFLOW

User registers (gets referral code)

Login → Dashboard

Search & follow users

Send Echo (+5 points)

Receive & Like Echo

Accept follow requests

Chat with connections

Gain referral points (+10)

View leaderboard

🎯 8️⃣ INNOVATION

✔ Focus on micro-interactions
✔ Gamified appreciation model
✔ Lightweight alternative to heavy social platforms
✔ Encourages positive engagement
✔ No ads, no algorithm overload

📈 9️⃣ FUTURE ENHANCEMENTS

• Real-time chat with WebSockets
• Mobile app version
• Cloud deployment (AWS / Render)
• Password hashing (bcrypt)
• Email verification
• Admin moderation panel
• Analytics dashboard
• Push notifications

🧠 🔟 LEARNING OUTCOMES

Through this project we learned:

• Full-stack web development
• Database schema design
• User authentication
• File handling in Flask
• Session management
• RESTful routing
• UI structuring
• Debugging & deployment basics

**Setup Instructions (Build Reproducibility)**
1.Clone the repository
2.Install dependencies: --> pip install flask
3.Run the application: --> python app.py
4.Open browser: [EchoVault](http://127.0.0.1:5000)
