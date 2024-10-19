import streamlit as st
import requests
import json
import os
import toml
import pandas as pd
from github_api import get_repo_commits
from database import init_db, get_commit_data

# 初始化数据库
init_db()

# 读取API密钥
file_path = 'credentials'
if os.path.exists(file_path):
    with open(file_path, 'r') as f:
        secrets = toml.load(f)
else:
    secrets = st.secrets

OPENROUTER_API_KEY = secrets['OPENROUTER']['OPENROUTER_API_KEY']

# 定义调用 GPT-4o-mini 的函数
def answer(system_prompt, user_prompt):
    msg = [
        {"role": "system", "content": system_prompt},
        {"role": "user", "content": user_prompt}
    ]
    
    response = requests.post(
        url="https://openrouter.ai/api/v1/chat/completions",
        headers={"Authorization": f"Bearer {OPENROUTER_API_KEY}"},
        data=json.dumps({
            "messages": msg,
            "model": "openai/gpt-4o-mini-2024-07-18"
        })
    )
    
    # 提取AI生成的响应
    resp = response.json()['choices'][0]['message']['content']
    return resp

# 应用标题
st.title("GitHub Classroom Tracker with AI")

# 用户输入 GitHub 仓库和 Token
repo = st.text_input("Enter the GitHub repository (e.g., user/repo):")
token = st.text_input("Enter your GitHub API token:", type="password")

# 用户输入需求
user_request = st.text_area("Enter your request or requirement:")

# 固定系统提示，用于引导AI如何生成结果
system_prompt = "You are an assistant that helps generate solutions based on user requirements. Respond clearly and concisely."

# 如果用户输入了仓库和token，调用GitHub API
if repo and token:
    st.write("Fetching commit data from GitHub...")
    commits = get_repo_commits(repo, token)
    
    # 将数据插入到数据库
    for commit in commits:
        get_commit_data(commit['commit']['message'], commit['commit']['author']['name'])

    st.write("Commit data fetched successfully!")

    # 获取并展示数据库中的数据
    data = get_commit_data()
    # 查看数据结构
    # st.write(data)

    df = pd.DataFrame(data, columns=["index", "Commit Message", "Author"])
    st.table(df)

    # 生成 AI 回答
    if st.button("Submit Request"):
        if user_request:
            # 调用AI，根据系统提示和用户需求生成响应
            ai_response = answer(system_prompt, user_request)
            st.write("AI's Response:")
            st.write(ai_response)
        else:
            st.warning("Please enter your request before submitting.")
