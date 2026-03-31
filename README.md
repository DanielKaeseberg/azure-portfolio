# Azure-based Portfolio

This repository contains the source code and infrastructure configuration for my website. The project is a full-stack serverless application hosted on Microsoft Azure.

## Architecture

The application is built using a serverless architecture on Azure, split into a frontend and a backend.

* **Frontend:** HTML, CSS, and plain JavaScript. Hosted as a static website.
* **Backend:** Python. Used to create an API that interacts with the database to track and update the visitor counter.
* **Database:** Uses the Azure Cosmos DB to update the visitor counter.
* **CI/CD:** GitHub Actions for automated testing and deployment.

## Technologies Used

* **HTML/CSS/JS:** Frontend structure and visitor counter logic.
* **Python:** Azure Functions for the backend API.
* **Azure Static Web Apps / Blob Storage:** Frontend hosting.
* **Azure Functions:** Serverless compute for the Python backend.
* **Azure Cosmos DB (Table API):** NoSQL database for the visitor counter.
* **GitHub Actions:** CI/CD pipeline.

## Setup and Deployment

### Prerequisites
* An Azure account.
* Azure CLI installed locally.
* Python 3.x installed.

### Local Development
1. Clone the repository: `git clone https://github.com/DanielKaeseberg/CloudResume.git`
2. Navigate to the backend directory and install dependencies: `pip install -r requirements.txt`
3. Run the Azure Function locally using Azure Functions Core Tools.
4. Open the `index.html` file in your browser to test the frontend connection to the local API.

### Deployment
This project uses GitHub Actions for CI/CD. Pushing to the `main` branch automatically triggers the deployment of the frontend to Azure Static Web Apps and the Python backend to Azure Functions.
