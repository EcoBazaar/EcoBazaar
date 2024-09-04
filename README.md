# EcoBazaar
**EcoBazaar is a sustainable e-commerce platform for buying and selling second-hand products, promoting eco-friendly choices and reducing waste.**
# **EcoBazaar**  

*EcoBazaar is a sustainable e-commerce platform for buying and selling second-hand products, promoting eco-friendly choices and reducing waste.*

---

## **Table of Contents**

1. [Introduction](#introduction)  
2. [Clone the Repository](#clone-the-repository)  
3. [Setup Instructions](#setup-instructions)  
   - [Creating a Virtual Environment](#creating-a-virtual-environment)  
   - [Activating the Virtual Environment](#activating-the-virtual-environment)  
   - [Installing Dependencies](#installing-dependencies)  
4. [Database Setup](#database-setup)  
   - [Making Migrations](#making-migrations)  
   - [Applying Migrations](#applying-migrations)  
5. [Running the Server](#running-the-server)  
6. [User Registration and Login](#user-registration-and-login)  
   - [Registering a New User](#registering-a-new-user)  
   - [Logging In](#logging-in)  
   - [Logout](#logout)  
7. [API Endpoints](#api-endpoints)  
8. [Testing with Postman](#testing-with-postman)  

---

## **Introduction**

EcoBazaar is a platform designed to encourage sustainable living by allowing users to buy and sell second-hand products. This README will guide you through the steps to set up, run, and interact with the project.

---

## **Clone the Repository**

First, clone the GitHub repository to your local machine. Open your terminal and run:

```bash
git clone https://github.com/username/ecobazaar.git
```
Replace `username` with your GitHub username.

Navigate into the project directory:

```bash
cd ecobazaar
```

---

## **Setup Instructions**

### **Creating a Virtual Environment**

To create a virtual environment, navigate to your project directory in the terminal and run the following command:

```bash
python -m venv venv
```

This command creates a virtual environment named `venv` in your project directory.

### **Activating the Virtual Environment**

Activate the virtual environment with the following command:

- **For Windows:**

  ```bash
  .\venv\Scripts\activate
  ```

- **For macOS/Linux:**

  ```bash
  source venv/bin/activate
  ```

### **Installing Dependencies**

With the virtual environment activated, install the required dependencies by running:

```bash
pip install -r requirements.txt
```

This command installs all the necessary packages listed in the `requirements.txt` file.

---

## **Database Setup**

### **Making Migrations**

To create migrations for the database, run:

```bash
python manage.py makemigrations
```

### **Applying Migrations**

After making the migrations, apply them to the database using:

```bash
python manage.py migrate
```

---

## **Running the Server**

To start the development server, execute the following command:

```bash
python manage.py runserver
```

The server will start running at `http://127.0.0.1:8000/` by default. You can access the application by navigating to this URL in your browser.

---

## **User Registration and Login**

### **Registering a New User**

1. Navigate to the registration page by visiting `http://127.0.0.1:8000/register/` in your browser.
2. Fill out the registration form with your username, email, and password.
3. Submit the form to create a new account.

### **Logging In**

1. After registering, you can log in by visiting `http://127.0.0.1:8000/login/`.
2. Enter your username and password.
3. Submit the form to log into your account.

### **Logout**

1. To log out of your account, visit `http://127.0.0.1:8000/logout/`.

---

## **API Endpoints**

Here are the available API endpoints for the EcoBazaar project:

- **`GET /api/products/`**  
  Retrieve a list of all products.
- **`POST /api/products/`**  
  Add a new product (requires authentication).
- **`GET /api/products/<id>/`**  
  Retrieve details of a specific product.
- **`PUT /api/products/<id>/`**  
  Update a specific product (requires authentication).
- **`DELETE /api/products/<id>/`**  
  Delete a specific product (requires authentication).
- **`POST /api/register/`**  
  Register a new user.
- **`POST /api/login/`**  
  Log in to obtain an authentication token.

*Ensure to replace `<id>` with the actual product ID when interacting with specific products.*

---

## **Testing with Postman**

To test the API, you can use the exported Postman workflow. Import the collection into Postman by following these steps:

1. Open Postman.
2. Click on **Import** in the top-left corner.
3. Select the file containing the exported workflow.
4. After importing, you can run the predefined requests to interact with the API.

Ensure that the server is running before testing the endpoints through Postman.

---

This README provides a comprehensive guide to setting up and running the EcoBazaar project, including how to register and log in as a user, and interact with the API endpoints. Adjust any specific URLs or paths according to your actual project setup.
