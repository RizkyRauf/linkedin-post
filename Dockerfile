FROM apify/actor-python-puppeteer:3.8

COPY . /opt/playwright/python/
WORKDIR /opt/playwright/python/

RUN pip install --no-cache-dir -r requirements.txt

CMD ["python", "main.py"]