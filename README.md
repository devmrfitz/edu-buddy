# Edu-Buddy
![](https://raw.githubusercontent.com/devmrfitz/edu-buddy/master/app/static/logo.png)

Edu-Buddy is an extension of SeeKer as well as a standalone product in itself. It is available at https://edu-buddy.herokuapp.com 

## Languages Used
<img src = "https://img.shields.io/badge/python%20-%236C0101.svg?style=for-the-badge&logo=python&logoColor=white" alt="python"/> <img src = "https://img.shields.io/badge/CSS-239120?&style=for-the-badge&logo=css3&logoColor=white" alt = "css"/> <img src = "https://img.shields.io/badge/HTML-orange?style=for-the-badge&logo=html5&logoColor=white" alt = "html"/>

## Installation
1) Fill up relevant API keys in .env_demo and rename it to .env.
2) Run 'heroku local'.

## How to add more courses?
Edu-Buddy has been made in such a way that you can (barring some exceptions) add your Google Classroom course to it without even needing to understand how it works.

This is how you can do it:
1) Find the CourseID of the course you want to add. To do this, go to https://developers.google.com/classroom/reference/rest/v1/courses/list?apix=true. Click on Execute and grant necessary permissions. Find ID of your course from the response you see.
2) Find topicID of the topic. To do this, go to https://developers.google.com/classroom/reference/rest/v1/courses.topics/list?apix=true. Enter the courseID and click on Execute. This will show you the topicID.
3) Now fork this repo, clone it and run <i>data_entry.py</i> (located in <i>app</i> folder). Enter the IDs and submit pull request.
