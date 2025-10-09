# Quick Bot
> _가볍고 편리한 디스코드 봇_

***

### 소개
Quick Bot은 디스코드 봇을 간단하고 가볍게 접근하기 위해  
사용자 친화적인 GUI를 통해 구현되었습니다.

### 실행 환경
봇은 실행되는 컴퓨터에서 작동되기에  
별도의 서버 호스팅 없이도 사용할 수 있습니다.

### 커스터마이징
봇이 처리하는 명령어와 이벤트 등을  
쉽게 커스텀할 수 있습니다.

### 모니터링
로그를 실시간으로 모니터링하고,  
봇의 실시간 상태를 확인할 수 있습니다.

### 목적
이는 초보자나 비개발자에게 디스코드 봇의 진입 장벽을 낮추고,  
소규모 서버 운영에 부담 없이 활용될 수 있습니다.

### GUI 편집
커맨드나 이벤트를 코드 편집이 아닌  
직관적인 GUI를 통해 수정할 수 있습니다.

## 실행 방법(for developers)

### Python 설치
Quick Bot은 Python을 기반으로 설계되었기에, 우선 파이썬을 설치해야 합니다.

> **Windows**
> ```
> $ winget install Python.Python.3.12
> ```

> **MacOS**
> ```
> $ brew install python@3.12
> ```

> **Ubuntu/Debian**
> ```
> $ sudo apt install python3.12 python3.12-venv -y
> ```

> **Fedora**
> ```
> $ sudo dnf install python3.12 python3.12-venv -y
> ```

> **Arch / Manjaro**
> ```
> $ sudo pacman -S python
> ```

### 라이브러리
Quick Bot을 실행하기 위해, 인터프리터에 라이브러리를 설치해야 합니다. 사용된 주요 라이브러리와 사용된 전체 라이브러리 설치 방법은 아래에서 확인할 수 있습니다.

> #### 사용된 주요 라이브러리
> - PyQt5 5.15.11 (GUI)
> - discord.py 2.6.2 (Discord API)
> - PyMySQL 1.1.2 (Database)
> - APScheduler 3.11.0 (Task Scheduling)
> - python-dotenv 1.1.1 (환경 변수 관리)
> - cryptography 45.0.6 (보안 관련)  
> - [전체 라이브러리](./requirements.txt)

#### 라이브러리 설치

> **Windows, Arch / Manjaro**
> ```
> $ python -m pip install -r requirements.txt
> ```

> **MacOS, Ubuntu/Debian, Fedora**
> ```
> $ python3 -m pip install -r requirements.txt
> ```

### 실행
메인 파일을 실행합니다.

> **Windows, Arch / Manjaro**
> ```
> $ python main.py
> ```

> **MacOS, Ubuntu/Debian, Fedora**
> ```
> $ python3 main.py
> ```

## 설치 방법
(아직 배포판은 공개되지 않음.)

## 문제가 발생했을 때
(기능구현 후 작성 예정.)

## 지원
만약, 문제가 생겼거나 지원이 필요할 때 개발자의 개인 이메일을 통해 연락할 수 있습니다.  
이메일: elin.ye.joon@gmail.com

## 포함된 pip 라이브러리
| 이름                                                       | 라이선스                               | 저작권                                                                       |
|:---------------------------------------------------------|:-----------------------------------|:--------------------------------------------------------------------------|
| [Discord.py](https://pypi.org/project/discord.py/)       | MIT License                        | Copyright (c) 2015-present Rapptz                                         |
| [APScheduler](https://pypi.org/project/APScheduler/)     | MIT License                        | Copyright (c) 2009 Alex Grönholm                                          |
| [python-dotenv](https://pypi.org/project/python-dotenv/) | BSD 3-Clause License               | Copyright (c) 2014 Saurabh Kumar, 2013 Ted Tieken, 2013 Jacob Kaplan-Moss |
| [cryptography](https://pypi.org/project/cryptography/)   | Apache-2.0 OR BSD-3-Clause License | Copyright (c) Individual contributors                                     |
| [PyQt5](https://pypi.org/project/PyQt5/)                 | GPL v3 OR Commercial License       | Copyright (c) Riverbank Computing Limited                                 |
| [pytest](https://pypi.org/project/pytest/)               | MIT License                        | Copyright (c) 2004 Holger Krekel and others                               |

## 라이선스
> **[MIT License 전문](./LICENSE)**
> ```
> MIT License
> Copyright (c) 2025 이예준
> 
> Permission is hereby granted, free of charge, to any person obtaining a copy
> of this software and associated documentation files (the "Software"), to deal
> in the Software without restriction, including without limitation the rights
> to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
> copies of the Software, and to permit persons to whom the Software is
> furnished to do so, subject to the following conditions:
> 
> The above copyright notice and this permission notice shall be included in all
> copies or substantial portions of the Software.
> 
> THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
> IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
> FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
> AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
> LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
> OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
> SOFTWARE.
> ```

## 개발 환경
- 운영체제: Windows 11
- IDE: PyCharmCE(Community Edition) 2024.1.7
- 언어: Python 3.12
- GUI 프레임워크: PyQt5 5.15.11 (Qt 5.15.2)
- 테스트 프레임워크: Pytest
- DB 라이브러리: SQLite3

## 릴리즈(변경 로그)
> ### [릴리즈 바로가기](https://github.com/pandamgay/gui_discord_bot/releases)

## 사용 예시
(기능구현 후 작성 예정.)
