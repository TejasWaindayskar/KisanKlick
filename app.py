import tkinter as tk
from tkinter import messagebox, filedialog
from PIL import Image, ImageTk
import tensorflow as tf
import numpy as np
import json
import os

# --- Load model ---
model = tf.keras.models.load_model("models/plant_disease_recog.keras")
with open("plant_disease.json", 'r') as f:
    plant_disease = json.load(f)
# --- Load or create users file ---
USER_FILE = "users.json"
if not os.path.exists(USER_FILE):
    with open(USER_FILE, 'w') as f:
        json.dump({}, f)

def load_users():
    with open(USER_FILE, 'r') as f:
        return json.load(f)

def save_users(users):
    with open(USER_FILE, 'w') as f:
        json.dump(users, f, indent=4)

# --- App Class ---
class PlantApp:
    def __init__(self, root):
        self.root = root
        self.root.title("🌿 Plant Disease Detector")
        self.root.geometry("600x700")
        self.root.configure(bg="#e8f5e9")
        self.user_data = None  # Logged-in user
        self.img_display = None
        self.uploaded_image_path = None

        self.init_frames()
        self.show_frame("login")

    def init_frames(self):
        self.frames = {}

        for frame_name in ["login", "signup", "home"]:
            frame = tk.Frame(self.root, bg="#e8f5e9")
            self.frames[frame_name] = frame
            frame.place(x=0, y=0, relwidth=1, relheight=1)

        self.build_login_frame()
        self.build_signup_frame()
        self.build_home_frame()

    def show_frame(self, name):
        frame = self.frames[name]
        frame.tkraise()

    def build_login_frame(self):
        f = self.frames["login"]
        tk.Label(f, text="Login", font=("Helvetica", 20, "bold"), bg="#e8f5e9").pack(pady=30)

        self.login_user = tk.StringVar()
        self.login_pass = tk.StringVar()

        tk.Label(f, text="Username", bg="#e8f5e9").pack()
        tk.Entry(f, textvariable=self.login_user).pack(pady=5)

        tk.Label(f, text="Password", bg="#e8f5e9").pack()
        tk.Entry(f, show="*", textvariable=self.login_pass).pack(pady=5)

        tk.Button(f, text="Login", bg="#66bb6a", fg="white", command=self.login).pack(pady=15)
        tk.Button(f, text="Don't have an account? Sign up", bg="#e8f5e9", fg="blue", command=lambda: self.show_frame("signup")).pack()

    def build_signup_frame(self):
        f = self.frames["signup"]
        tk.Label(f, text="Signup", font=("Helvetica", 20, "bold"), bg="#e8f5e9").pack(pady=30)

        self.signup_name = tk.StringVar()
        self.signup_user = tk.StringVar()
        self.signup_email = tk.StringVar()
        self.signup_pass = tk.StringVar()
        self.signup_plants = tk.StringVar()

        tk.Label(f, text="Name", bg="#e8f5e9").pack()
        tk.Entry(f, textvariable=self.signup_name).pack(pady=5)

        tk.Label(f, text="Username", bg="#e8f5e9").pack()
        tk.Entry(f, textvariable=self.signup_user).pack(pady=5)

        tk.Label(f, text="Email", bg="#e8f5e9").pack()
        tk.Entry(f, textvariable=self.signup_email).pack(pady=5)

        tk.Label(f, text="Password", bg="#e8f5e9").pack()
        tk.Entry(f, show="*", textvariable=self.signup_pass).pack(pady=5)

        tk.Label(f, text="Plants you grow (comma-separated)", bg="#e8f5e9").pack()
        tk.Entry(f, textvariable=self.signup_plants).pack(pady=5)

        tk.Button(f, text="Sign Up", bg="#66bb6a", fg="white", command=self.signup).pack(pady=15)
        tk.Button(f, text="Already have an account? Login", bg="#e8f5e9", fg="blue", command=lambda: self.show_frame("login")).pack()

    def build_home_frame(self):
        f = self.frames["home"]
        self.welcome_label = tk.Label(f, text="", font=("Helvetica", 16), bg="#e8f5e9")
        self.welcome_label.pack(pady=10)

        self.plants_label = tk.Label(f, text="", bg="#e8f5e9", fg="gray")
        self.plants_label.pack()

        tk.Button(f, text="Upload Leaf Image", bg="#66bb6a", fg="white", command=self.upload_image).pack(pady=10)
        self.img_label = tk.Label(f, bg="#e8f5e9")
        self.img_label.pack()

        tk.Button(f, text="Predict Disease", bg="#43a047", fg="white", command=self.predict_disease).pack(pady=10)
        self.result_label = tk.Label(f, text="", font=("Helvetica", 14), bg="#e8f5e9", fg="darkgreen")
        self.result_label.pack(pady=20)

        tk.Button(f, text="Logout", bg="red", fg="white", command=self.logout).pack(side="bottom", pady=10)

    def login(self):
        users = load_users()
        username = self.login_user.get()
        password = self.login_pass.get()

        if username in users and users[username]["password"] == password:
            self.user_data = users[username]
            self.user_data["username"] = username
            self.update_home_screen()
            self.show_frame("home")
        else:
            messagebox.showerror("Login Failed", "Invalid credentials.")

    def signup(self):
        users = load_users()
        username = self.signup_user.get()

        if username in users:
            messagebox.showerror("Signup Error", "Username already exists.")
            return

        users[username] = {
            "name": self.signup_name.get(),
            "email": self.signup_email.get(),
            "password": self.signup_pass.get(),
            "plants": self.signup_plants.get().split(",")
        }

        save_users(users)
        messagebox.showinfo("Success", "Account created! Please login.")
        self.show_frame("login")

    def update_home_screen(self):
        name = self.user_data["name"]
        plants = ", ".join(self.user_data.get("plants", []))
        self.welcome_label.config(text=f"Welcome, {name}!")
        self.plants_label.config(text=f"🌱 Your Plants: {plants}")

    def logout(self):
        self.user_data = None
        self.login_user.set("")
        self.login_pass.set("")
        self.show_frame("login")

    def upload_image(self):
        file_path = filedialog.askopenfilename(filetypes=[("Images", "*.jpg *.jpeg *.png")])
        if file_path:
            self.uploaded_image_path = file_path
            img = Image.open(file_path)
            img = img.resize((250, 250))
            self.img_display = ImageTk.PhotoImage(img)
            self.img_label.config(image=self.img_display)
            self.result_label.config(text="")

    def predict_disease(self):
        if not self.uploaded_image_path:
            messagebox.showerror("No Image", "Upload a leaf image first.")
            return

        image = tf.keras.utils.load_img(self.uploaded_image_path, target_size=(160, 160))
        feature = tf.keras.utils.img_to_array(image)
        feature = np.expand_dims(feature, axis=0)
        prediction = model.predict(feature)
        predicted_index = str(np.argmax(prediction))
        label = plant_disease[predicted_index]
        #label = plant_disease[prediction.argmax()]
        self.result_label.config(text=f"🦠 Prediction: {label}")

# --- Launch ---
root = tk.Tk()
app = PlantApp(root)
root.mainloop()
