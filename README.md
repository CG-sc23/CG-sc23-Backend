# CG-sc23-Backend

DOMO 서비스 구현을 위한 Back-End Repository 입니다.

## 기술 스택
### Framework
* Django, DRF
### CI/CD
* Github Action
### Issue tracker
* Sentry
### AWS
* EC2, S3, Load Balancer, Route 53, CM
### etc
* Celery, RabbitMQ

## 설치 방법
1. `git clone {repository url}`
2. `pip install poetry`
3. `poetry install`
4. `poetry shell`
5. `python manage.py makemigrations`
6. `python manage.py migrate`
7. `python manage.py runserver` (환경변수 설정 필요)

## Test 방법
`python manage.py test --parallel`
