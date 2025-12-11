-pip install django djangorestframework djangorestframework-simplejwt django-cors-headers pillow django-jazzmin django-environ
-django-admin startproject core .
-python manage.py makemigrations
python manage.py migrate
-Email: admin@example.com Password: admin123
-pip install django-allauth dj-rest-auth
-pip install requests
-pip install cryptography pyjwt

GOOGLE AUTH:
-It is normal to feel unsure here because this part happens outside of your code editor.

1. Whose email should you use?
Use YOUR own Google email address.

Why? You are currently the "Developer." You need full control to change settings instantly. If you use the client's email, Google might ask for 2-Factor Authentication codes sent to the client's phone, which will block you.

Can I change it later? Yes. Once the project is finished, you can add the client's email as an "Owner" and remove yourself. For now, keep it on your account.

2. Step-by-Step Guide (Simplified)
I will walk you through this slowly. Open a new browser tab and follow along.

Phase A: Create the Project
Go to console.cloud.google.com.

Log in with your Gmail.

In the top-left (next to the Google Cloud logo), click the dropdown menu (it might say "Select a project").

Click New Project (top right of the popup).

Project Name: Vinsaraa-Dev (or similar).

Click Create. (Wait a few seconds for it to finish).

Phase B: The "Consent Screen" (What users see)
In the top-left dropdown, select the new Vinsaraa project you just created.

In the left sidebar, click APIs & Services > OAuth consent screen.

User Type: Choose External.

Click Create.

App Information:

App name: Vinsaraa

User support email: Select your email.

Developer contact information: Type your email again.

Click Save and Continue (You can skip the "Scopes" and "Test Users" pages—just keep clicking Save/Next until you are done).

Phase C: Get the Keys (The Important Part)
On the left sidebar, click Credentials.

Click + CREATE CREDENTIALS (top of screen) > OAuth client ID.

Application type: Select Web application.

Name: React Frontend (or leave default).

Authorized JavaScript origins:

Click ADD URI.

Type: http://localhost:3000 (This is where your React site will live).

Authorized redirect URIs:

Click ADD URI.

Type: http://localhost:3000

Click CREATE.

Phase D: Copy the Keys
A popup will appear with two long codes. Do not close this window yet.

Client ID: Copy this string.

Client Secret: Copy this string.

3. Put them into Django
Now go back to your Django Admin panel (http://127.0.0.1:8000/admin/).

Click Social applications (under Social Accounts).

Click Add Social application.

Provider: Choose Google.

Name: Type Google.

Client id: Paste the long Client ID you just copied.

Secret key: Paste the Client Secret you just copied.

Sites: Move example.com from the left box to the right box.

Save.

Once you hit Save, you are officially done with the Google Backend setup!

Let me know once you have saved it, and we can finally start the Frontend (React)!
-Client ID:44114483480-qullmaqkm953nief34vhmmtik3g4d2e3.apps.googleusercontent.com
-Client Secret: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