# ReplyPilot

**ReplyPilot** - Reply to all reviews on Autopilot using OpenAI

ReplyPilot is a Django-based open-source project designed to automate the process of replying to customer reviews. By using OpenAI's language models, ReplyPilot helps businesses save time by generating thoughtful, context-aware responses to reviews automatically.

## Features

- **Automated Review Replies**: Automatically generate replies for customer reviews using OpenAI.
- **Multiple Apps & Users**: Manage replies for multiple apps and users from a single interface.
- **Admin Dashboard**: Setup apps, check all reviews, and monitor generated replies in a centralized admin area.
- **Standalone Application**: No integrations required—just install and use.
- **Django Framework**: Built with Django for easy extensibility and scalability.
  
### Current Limitations

- **Platform Support**: Currently supports Google Play reviews only (additional platforms coming soon).

## Installation

To get started with ReplyPilot, follow these steps:

1. **Clone the repository**:
   ```bash
   git clone https://github.com/Romamo/replypilot.git
   cd replypilot
   '''

2. **Install dependencies**: Ensure you have pip and virtualenv installed. Then create a virtual environment and install the dependencies:
   ```bash
   virtualenv venv
   source venv/bin/activate
   pip install -r requirements.txt
   ```

3. **Set up environment variables**: Create a .env file in the root directory with your OpenAI API key:
    ```bash
    OPENAI_API_KEY=your_openai_api_key
    ```

4. **Run Django migrations**: Apply the necessary database migrations:
    ```bash
    python manage.py migrate
    ```
   
5. **Create a superuser**: To access the admin dashboard, create an admin user:
    ```bash
    python manage.py createsuperuser
    ```
6. **Run the application**: Start the Django development server:
    ```bash
    python manage.py runserver
    ```
7. **Access the Admin Dashboard**: Navigate to http://127.0.0.1:8000/admin and log in using your superuser credentials. From here, you can set up apps, manage reviews, and view replies.   

## Usage
Once the application is running, follow these steps to generate automatic replies for your Google Play reviews:
1. **Add your apps**: Use the admin dashboard to add your Google Play apps.
2. **Review Management**: The app will automatically fetch reviews from your linked Google Play accounts.
3. **Generate Replies**: Replies will be automatically generated for each review, and you can either approve and modify them or have them posted automatically.

## Configuration

ReplyPilot offers several customization options:

1. **Tone Settings**: Choose between formal, casual, or other tones for your replies.
2. **Multiple Users**: Manage multiple consoles or users to handle replies for different apps.
3. **Custom Review Approval**: You can opt to review and approve replies before posting.

## Roadmap

* Add support for more review platforms (Google Reviews, Yelp, Amazon, etc.).
* Web-based UI for managing replies and users outside of Django Admin.
* Add advanced analytics to track trends and sentiments in reviews.
 
## License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.
