# BharatFD FAQs Documentation

## Overview

BharatFD FAQs is a Django-based backend application designed to manage multilingual FAQs. The project includes:

- **Multilingual Support**: Automated translations using Google Translate API.
- **WYSIWYG Editor**: Integration with django-ckeditor for rich text editing.
- **REST API**: Exposes endpoints for retrieving FAQs in different languages.
- **Caching**: Utilizes Redis for improved performance.
- **Custom Admin Panel**: Provides a user-friendly interface for managing FAQs.
- **Docker Support**: Enables easy deployment using Docker and docker-compose.

---

## Table of Contents

1. [Installation](#installation)
2. [API Usage](#api-usage)
3. [Contribution Guidelines](#contribution-guidelines)
4. [License](#license)

---

## 1. Installation

### Prerequisites

- Python 3.9+
- PostgreSQL (Optional)
- Redis (for caching)
- Docker & Docker Compose (for containerized deployment)

### Steps

1. **Clone the repository:**

   ```sh
   git clone <repository_url>
   cd BharatFD_faqs
   ```

2. **Create a virtual environment:**

   ```sh
   python -m venv env
   source env/bin/activate  # macOS/Linux
   env\Scripts\activate  # Windows
   ```

3. **Install dependencies:**

   ```sh
   pip install -r requirements.txt
   ```

4. **Run migrations:**

   ```sh
   python manage.py migrate
   ```

5. **Run the server:**
   ```sh
   python manage.py runserver
   ```

---

# FAQ API Documentation

## 2. API Usage

### Fetch FAQs

- **Default (English)**
  ```sh
  curl http://localhost:8000/api/faqs/
  ```
- **Hindi Translation**
  ```sh
  curl http://localhost:8000/api/faqs/?lang=hi
  ```
- **Bengali Translation**
  ```sh
  curl http://localhost:8000/api/faqs/?lang=bn
  ```

#### Pagination

- The API supports pagination with 5 FAQs per page.
- Use the `page` query parameter to navigate between pages.
  ```sh
  curl http://localhost:8000/api/faqs/?page=2
  ```

#### Response Structure

```json
{
  "count": 20,
  "total_pages": 4,
  "current_page": 1,
  "next": true,
  "previous": false,
  "results": [
    {
      "id": 1,
      "question": "What is this API?",
      "answer": "This API manages FAQs.",
      "question_translated": "इस एपीआई का क्या उपयोग है?",
      "answer_translated": "यह एपीआई अक्सर पूछे जाने वाले प्रश्नों को प्रबंधित करता है।",
      "created_at": "2024-08-11T12:00:00Z",
      "updated_at": "2024-08-11T12:30:00Z"
    }
  ]
}
```

### Create an FAQ

#### Request

```sh
curl -X POST http://localhost:8000/api/faqs/ \n -H "Content-Type: application/json" \n -d '{
  "question": "What is caching?",
  "answer": "Caching stores frequently used data for quick access.",
  "question_translated": "कैशिंग क्या है?",
  "answer_translated": "कैशिंग अक्सर उपयोग किए जाने वाले डेटा को तेजी से एक्सेस करने के लिए संग्रहीत करता है।"
}'
```

#### Response

```json
{
  "id": 2,
  "question": "What is caching?",
  "answer": "Caching stores frequently used data for quick access.",
  "question_translated": "कैशिंग क्या है?",
  "answer_translated": "कैशिंग अक्सर उपयोग किए जाने वाले डेटा को तेजी से एक्सेस करने के लिए संग्रहीत करता है।",
  "created_at": "2024-08-11T13:00:00Z",
  "updated_at": "2024-08-11T13:00:00Z"
}
```

### Fetch a Single FAQ

```sh
curl http://localhost:8000/api/faqs/1/
```

#### Response

```json
{
  "id": 1,
  "question": "What is this API?",
  "answer": "This API manages FAQs.",
  "question_translated": "इस एपीआई का क्या उपयोग है?",
  "answer_translated": "यह एपीआई अक्सर पूछे जाने वाले प्रश्नों को प्रबंधित करता है।",
  "created_at": "2024-08-11T12:00:00Z",
  "updated_at": "2024-08-11T12:30:00Z"
}
```

### Update an FAQ

#### Request (Full Update)

```sh
curl -X PUT http://localhost:8000/api/faqs/1/ \n -H "Content-Type: application/json" \n -d '{
  "question": "What is caching in web applications?",
  "answer": "Caching is a technique to store copies of frequently accessed data.",
  "question_translated": "वेब अनुप्रयोगों में कैशिंग क्या है?",
  "answer_translated": "कैशिंग एक तकनीक है जो अक्सर एक्सेस किए जाने वाले डेटा की प्रतियां संग्रहीत करती है।"
}'
```

#### Response

```json
{
  "id": 1,
  "question": "What is caching in web applications?",
  "answer": "Caching is a technique to store copies of frequently accessed data.",
  "question_translated": "वेब अनुप्रयोगों में कैशिंग क्या है?",
  "answer_translated": "कैशिंग एक तकनीक है जो अक्सर एक्सेस किए जाने वाले डेटा की प्रतियां संग्रहीत करती है।",
  "created_at": "2024-08-11T12:00:00Z",
  "updated_at": "2024-08-11T13:15:00Z"
}
```

### Partial Update an FAQ

#### Request

```sh
curl -X PATCH http://localhost:8000/api/faqs/1/ \n -H "Content-Type: application/json" \n -d '{
  "answer": "Caching improves performance by reducing database queries."
}'
```

#### Response

```json
{
  "id": 1,
  "question": "What is caching in web applications?",
  "answer": "Caching improves performance by reducing database queries.",
  "question_translated": "वेब अनुप्रयोगों में कैशिंग क्या है?",
  "answer_translated": "कैशिंग एक तकनीक है जो अक्सर एक्सेस किए जाने वाले डेटा की प्रतियां संग्रहीत करती है।",
  "created_at": "2024-08-11T12:00:00Z",
  "updated_at": "2024-08-11T13:20:00Z"
}
```

### Delete an FAQ

#### Request

```sh
curl -X DELETE http://localhost:8000/api/faqs/1/
```

#### Response

```json
{
  "message": "FAQ with id 1 has been successfully deleted.",
  "status": "success"
}
```

## 3. Redis Caching

- The FAQ list is cached in Redis with the key format: `faqs:list:{lang}`.
- Deleting or updating an FAQ clears the cache for consistency.
- Individual FAQ entries are cached with `faq:{id}`.

## 4. Home Page View

- The home page renders FAQs with language translation support.
- Uses Django's built-in paginator to display FAQs.

---

This API documentation provides an overview of the endpoints and their usage for managing FAQs effectively.

## 3. Contribution Guidelines

We welcome contributions! To contribute, follow these steps:

1. **Fork the repository** on GitHub.
2. **Create a new branch** for your feature:
   ```sh
   git checkout -b feature-branch-name
   ```
3. **Commit changes** following conventional commit messages:
   ```sh
   git commit -m "feat: Add new FAQ feature"
   ```
4. **Push to your fork**:
   ```sh
   git push origin feature-branch-name
   ```
5. **Open a Pull Request (PR)** to the main repository.

---

## 4. License

This project is licensed under the MIT License. See the `LICENSE` file for details.
