# COMP5241_Group_Project_18
## Information
Group members:  
Xiaodong Lin  
Zhenwei Zhou  
Yutong Jiang  
Lan Luo  
Yuhao Bao  

# GitHub Classroom Tracker

A web application prototype that helps instructors track student group progress and collaboration in GitHub repositories. The app fetches activity data such as commits, issues, and pull requests from GitHub, visualizes it in a dashboard, and uses OpenAI to generate performance summaries.

## Features

- Track and visualize GitHub activities (commits, issues, pull requests).
- Store activity data in SQLite.
- Generate performance summaries using OpenAI GPT-3/GPT-4.
- Provide insights into individual and group contributions.

## Technology Stack

- **Frontend**: Streamlit (for dashboard and visualizations)
- **Backend**: Flask (for handling API requests)
- **Database**: SQLite (to store activity data)
- **API**: GitHub API (to fetch repository data), OpenAI API (for generating summaries)

## Setup

### Prerequisites

- Python 3.x
- GitHub personal access token
- OpenAI API key

### Installation

1. Clone the repository:
    ```bash
    git clone https://github.com/jytpolyu/COMP5241_Group_Project_18.git
    cd COMP5241_Group_Project_18
    ```

2. Install dependencies:
    ```bash
    pip install -r requirements.txt
    ```

3. Run the Streamlit app:
    ```bash
    streamlit run app.py
    ```

4. (Optional) Start the Flask backend:
    ```bash
    python backend.py
    ```

## Usage

- Enter the GitHub repository and your API token in the Streamlit app to fetch and display commit data.
- Generate AI-powered performance summaries based on the data.


