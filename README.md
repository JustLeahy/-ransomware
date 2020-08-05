# SQLGitHub

SQLGitHub — Managing GitHub organization made easier


## Introduction

SQLGitHub features a SQL-like syntax that allows you to:   
**Query information about an organization as a whole.**

You may also think of it as a better, enhanced frontend layer built on top of GitHub's RESTful API.

- [Presentation](assets/slides.pdf)
- [Poster](assets/poster.pdf)

![ScreenshotIntro](https://i.imgur.com/Ii355Ds.png)


## Installation

1. Install prerequisites  
```bash
pip install requests prompt_toolkit pygments regex
```

2. Install my patched PyGithub  
```bash
git clone https://github.com/lnishan/PyGithub.git
cd PyGithub
./setup.py build
sudo ./setup.py install
```

3. Configure SQLGitHub (optional)  
In root directory (same directory as `SQLGitHub.py`),  
Create and edit `config.py`:  
```python
token = "your token here"  # can be obtained from https://github.com/settings/tokens
output = "str"  # or "csv", "html"
```

4. Start SQLGitHub  
```bash
./SQLGitHub.py
```

## Sample Usage

### → Get name and description from all the repos in [abseil